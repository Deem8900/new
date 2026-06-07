"""
ui/components.py — Reusable UI components shared across all pages.

Rule: static HTML goes in st.markdown (self-contained, no open tags).
      Interactive widgets (buttons, expanders) are always native Streamlit,
      called AFTER closing any HTML block.
"""

import streamlit as st
import pandas as pd

from engine.time_utils import DAY_NAMES
from ui.styles import LOGO

# Medal labels for ranked section cards
RANK_LABELS = {
    0: "🥇 1st Best Match",
    1: "🥈 2nd Best Match",
    2: "🥉 3rd Best Match",
}

# Notification icon mapping
NOTIF_ICONS = {
    "add_course": ("➕", "notif-icon-add"),
    "drop_course": ("🗑️", "notif-icon-drop"),
    "change_section": ("🔄", "notif-icon-change"),
    "withdrawal": ("⚠️", "notif-icon-drop"),
    "message": ("💬", "notif-icon-msg"),
    "info": ("ℹ️", "notif-icon-info"),
}


# ── Navbar ────────────────────────────────────────────────────────────────────

def nav(right_html: str = "") -> None:
    st.markdown(
        f'<div class="uoh-nav">'
        f'<div class="uoh-nav-left">'
        f'  <img class="uoh-nav-logo" src="{LOGO}">'
        f'  <div><div class="uoh-nav-brand">AcademiQ</div>'
        f'  <div class="uoh-nav-sub">Smart Academic Advising · University of Hail</div></div>'
        f'</div>'
        f'<div class="uoh-nav-right">{right_html}</div></div>',
        unsafe_allow_html=True,
    )


# ── Breadcrumb ────────────────────────────────────────────────────────────────

def breadcrumb(items: list[tuple[str, str | None]]) -> None:
    """
    Render a breadcrumb trail.
    items = [(label, page_key_or_None), ...]  — last item is current page.
    """
    parts = []
    for i, (label, _) in enumerate(items):
        if i == len(items) - 1:
            parts.append(f'<span class="uoh-bread-curr">{label}</span>')
        else:
            parts.append(f'<span class="uoh-bread-item">{label}</span>')
            parts.append('<span class="uoh-bread-sep">›</span>')
    st.markdown(
        '<div class="uoh-bread">' + "".join(parts) + "</div>",
        unsafe_allow_html=True,
    )


# ── Section title ─────────────────────────────────────────────────────────────

def sec_title(icon: str, label: str, sub: str = "") -> None:
    sub_html = f'<div class="uoh-sec-sub">{sub}</div>' if sub else ""
    st.markdown(
        f'<div class="uoh-sec-title">'
        f'<div class="uoh-sec-icon">{icon}</div>'
        f'<div><div class="uoh-sec-label">{label}</div>{sub_html}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ── Info / warn boxes ─────────────────────────────────────────────────────────

def info(msg: str) -> None:
    st.markdown(f'<div class="box-info">ℹ️ &nbsp;{msg}</div>', unsafe_allow_html=True)


def warn(msg: str) -> None:
    st.markdown(f'<div class="box-warn">⚠️ &nbsp;{msg}</div>', unsafe_allow_html=True)


def hr() -> None:
    st.markdown('<hr class="uoh-divider">', unsafe_allow_html=True)


# ── Stars HTML (used inside cards — renders inside HTML, so must stay HTML) ───

def stars_html(n: int) -> str:
    n = max(1, min(5, n))
    return (
        f'<span style="color:#fbbf24">{"★" * n}</span>'
        f'<span style="color:rgba(255,255,255,.25)">{"☆" * (5 - n)}</span>'
    )


# ── Schedule table ────────────────────────────────────────────────────────────

def schedule_table(df: pd.DataFrame) -> None:
    """
    Render the student's schedule as a styled HTML table.
    Columns: Ref No., Code, Course Name, Hrs, Day, Start, End, Location, Type
    The Ref No. (CRN) column is rendered in navy.
    """
    if df.empty:
        st.info("No registered sections found for this semester.")
        return

    headers = ["Ref No.", "Code", "Course Name", "Hrs", "Day", "Start", "End", "Location", "Type"]
    rows_html = ""
    for _, r in df.iterrows():
        typ      = str(r.get("type", "LEC")).upper()
        tag      = "type-lec" if typ == "LEC" else "type-lab"
        day_code = str(r.get("Days") or "—")
        day_full = DAY_NAMES.get(day_code, day_code)
        rows_html += (
            "<tr>"
            f"<td class='ref-col'>{r.get('Cec', '—')}</td>"
            f"<td><b>{r.get('Code', '—')}</b></td>"
            f"<td style='text-align:left'>{r.get('Course_name', '—')}</td>"
            f"<td>{r.get('Hours', '—')}</td>"
            f"<td><b>{day_code}</b>"
            f"<br><span style='font-size:.7rem;color:#94a3b8'>{day_full}</span></td>"
            f"<td>{r.get('STime', '—')}</td>"
            f"<td>{r.get('ETim', '—')}</td>"
            f"<td>{r.get('Location', '—')}</td>"
            f"<td><span class='{tag}'>{typ}</span></td>"
            "</tr>"
        )

    header_cells = "".join(f"<th>{h}</th>" for h in headers)
    st.markdown(
        f'<div class="sched-wrap">'
        f'<table class="sched-tbl">'
        f'<thead><tr>{header_cells}</tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        f'</table></div>',
        unsafe_allow_html=True,
    )


# ── Section card ──────────────────────────────────────────────────────────────

def section_card(row: dict, rank: int, btn_label: str, key: str) -> bool:
    """
    Render a ranked section card.
    Returns True if the user clicked the select button.

    Wrapped in st.container() to give React a stable anchor and prevent
    the removeChild DOM reconciliation error on page rerenders.
    """
    score   = int(row.get("Score", 3))
    typ     = str(row.get("Type", "LEC")).upper()
    tag_cls = "type-lec" if typ == "LEC" else "type-lab"
    seats   = row.get("Seats", "—")
    seats_c = "seats-hi" if isinstance(seats, int) and seats >= 10 else "seats-lo"
    day_nm  = row.get(
        "Day_name",
        DAY_NAMES.get(str(row.get("Days", "")), str(row.get("Days", ""))),
    )
    rank_lbl = RANK_LABELS.get(rank, f"Option {rank + 1}")

    clicked = False
    with st.container():
        st.markdown(f"""
<div class="sec-card">
  <div class="sec-card-head">
    <div>
      <div class="sec-rank">{rank_lbl}</div>
      <div class="sec-crn">
        CRN &nbsp;{row['Cec']}&nbsp;
        <span class="{tag_cls}" style="font-size:.7rem;padding:2px 8px">{typ}</span>
      </div>
      <div class="sec-name">{row.get('Code','—')} &mdash; {row.get('Course_name','—')}</div>
    </div>
    <div class="sec-stars-wrap">
      <div class="sec-stars">{stars_html(score)}</div>
      <div class="sec-score-lbl">AI Score &nbsp;{score} / 5</div>
    </div>
  </div>
  <div class="sec-card-body">
    <div class="sec-grid">
      <div class="sec-gi"><div class="gi-lbl">📅 Day</div>
        <div class="gi-val">{day_nm}</div></div>
      <div class="sec-gi"><div class="gi-lbl">⏰ Start – End</div>
        <div class="gi-val">{row.get('STime','—')} – {row.get('ETim','—')}</div></div>
      <div class="sec-gi"><div class="gi-lbl">📍 Location</div>
        <div class="gi-val">{row.get('Location','—')}</div></div>
      <div class="sec-gi"><div class="gi-lbl">💺 Open Seats</div>
        <div class="gi-val {seats_c}">{seats}</div></div>
      <div class="sec-gi"><div class="gi-lbl">👩‍🏫 Instructor</div>
        <div class="gi-val">{row.get('Instructor','—')}</div></div>
      <div class="sec-gi"><div class="gi-lbl">📚 Credit Hrs</div>
        <div class="gi-val">{row.get('Hours','—')}</div></div>
      <div class="sec-gi"><div class="gi-lbl">🏫 Type</div>
        <div class="gi-val"><span class="{tag_cls}">{typ}</span></div></div>
      <div class="sec-gi"><div class="gi-lbl">⭐ Rating</div>
        <div class="gi-val">{"⭐" * score} ({score}/5)</div></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        if row.get("Criteria"):
            with st.expander("📊 View score breakdown"):
                for line in row["Criteria"]:
                    st.write(line)

        _, col_btn, _ = st.columns([3, 2, 3])
        clicked = col_btn.button(btn_label, key=key,
                                 use_container_width=True, type="primary")
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    return clicked


# ── Notification panel ────────────────────────────────────────────────────────

def render_notification_panel(recipient_type: str, recipient_id: int) -> None:
    """
    Render an expandable notification panel showing recent notifications.
    Works for both students and advisors.
    """
    try:
        from db.notifications import get_notifications, get_unread_count, mark_all_read
    except Exception:
        return

    try:
        unread = get_unread_count(recipient_type, recipient_id)
        notifications = get_notifications(recipient_type, recipient_id, limit=15)
    except Exception:
        return

    if not notifications and unread == 0:
        return

    badge_html = (
        f' <span class="notif-badge">{unread}</span>' if unread > 0 else ""
    )

    with st.expander(f"🔔 Notifications{' (' + str(unread) + ' new)' if unread else ''}", expanded=(unread > 0)):
        if not notifications:
            st.markdown(
                '<div style="text-align:center;color:#94a3b8;padding:16px">'
                'No notifications yet.</div>',
                unsafe_allow_html=True,
            )
            return

        items_html = []
        for n in notifications:
            ntype = str(n.get("notif_type", "info"))
            icon_emoji, icon_cls = NOTIF_ICONS.get(ntype, ("ℹ️", "notif-icon-info"))
            is_read = int(n.get("is_read", 0))
            item_cls = "notif-item-read" if is_read else "notif-item-unread"
            title = n.get("title", "")
            body = n.get("body", "")
            ts = n.get("created_at", "")

            items_html.append(
                f'<div class="notif-item {item_cls}">'
                f'  <div class="notif-icon {icon_cls}">{icon_emoji}</div>'
                f'  <div>'
                f'    <div class="notif-title">{title}</div>'
                f'    <div class="notif-body">{body}</div>'
                f'    <div class="notif-time">{ts}</div>'
                f'  </div>'
                f'</div>'
            )

        st.markdown(
            '<div class="notif-panel">'
            + "".join(items_html)
            + '</div>',
            unsafe_allow_html=True,
        )

        if unread > 0:
            if st.button("✓ Mark All as Read", key=f"mark_read_{recipient_type}_{recipient_id}"):
                mark_all_read(recipient_type, recipient_id)
                st.rerun()


# ── Enhanced chat bubble rendering ────────────────────────────────────────────

def render_chat_bubble(msg: dict, viewer_role: str = "student") -> None:
    """
    Render an enhanced chat bubble.
    viewer_role: 'student' or 'advisor' — determines alignment.
    """
    sender_role = str(msg.get("sender_role", "")).lower()
    sender_name = msg.get("sender_name") or sender_role.title()
    body = msg.get("body", "")
    ts = msg.get("timestamp", "")
    action_type = msg.get("action_type")
    action_crn = msg.get("action_crn")
    handled = int(msg.get("handled") or 0)

    # Student messages align right for student viewer, left for advisor viewer
    if viewer_role == "student":
        align_right = (sender_role == "student")
    else:
        align_right = (sender_role == "advisor")

    align = "right" if align_right else "left"
    bubble_cls = "chat-bubble-student" if sender_role == "student" else "chat-bubble-advisor"

    action_html = ""
    if action_type and action_crn is not None:
        status = "✅ Handled" if handled else "⏳ Pending"
        action_html = (
            f'<div class="chat-bubble-action">'
            f'<b>📌 Request:</b> {action_type.upper()} CRN {int(action_crn)} '
            f'&nbsp;·&nbsp; {status}'
            f'</div>'
        )

    st.markdown(
        f'<div style="text-align:{align}">'
        f'  <div class="{bubble_cls}">'
        f'    <div class="chat-bubble-meta">'
        f'      {sender_name} &nbsp;·&nbsp; {ts}'
        f'    </div>'
        f'    <div class="chat-bubble-body">{body}</div>'
        f'    {action_html}'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_chat_empty_state() -> None:
    """Render a nice empty state for chats."""
    st.markdown(
        '<div class="chat-empty-state">'
        '  <div class="chat-empty-icon">💬</div>'
        '  <div>No messages yet — start the conversation below.</div>'
        '</div>',
        unsafe_allow_html=True,
    )


# ── Floating Academic-Advisor chat widget (FAB + popup dialog) ────────────────

def _render_chat_dialog_body(advisor_id: int, sid: int, student_name: str,
                             advisor_name: str = "Academic Advisor") -> None:
    """Render the chat UI inside the popup dialog (called by st.dialog)."""
    import streamlit as st
    from db.advisor import get_messages, send_message

    # Distinctive header strip
    st.markdown(
        f'<div class="uoh-chat-modal-head">'
        f'  <div class="uoh-chat-modal-avatar">🎓</div>'
        f'  <div>'
        f'    <div class="uoh-chat-modal-title">{advisor_name}</div>'
        f'    <div class="uoh-chat-modal-sub">'
        f'      <span class="uoh-chat-status-dot"></span>'
        f'      Academic Advisor &nbsp;·&nbsp; usually replies within a day'
        f'    </div>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Pending-clear pattern (avoids the StreamlitAPIException when clearing
    #    a widget value after the widget has already been instantiated) ──
    body_key = f"_fab_chat_body_{sid}"
    if st.session_state.pop(f"_clear_{body_key}", False):
        st.session_state[body_key] = ""

    # Conversation thread
    msgs = get_messages(int(advisor_id), int(sid))
    bubbles = ['<div class="uoh-chat-scroll">']
    if not msgs:
        bubbles.append(
            '<div class="chat-empty-state">'
            '  <div class="chat-empty-icon">💬</div>'
            '  <div>No messages yet — start the conversation below.</div>'
            '</div>'
        )
    else:
        for m in msgs:
            role = str(m.get("sender_role", "")).lower()
            sender_name_msg = m.get("sender_name") or role.title()
            body = m.get("body", "")
            ts = m.get("timestamp", "")
            align = "right" if role == "student" else "left"
            bubble_cls = "chat-bubble-student" if role == "student" else "chat-bubble-advisor"

            action_html = ""
            if m.get("action_type") and m.get("action_crn") is not None:
                status = "✅ Handled" if int(m.get("handled") or 0) else "⏳ Pending"
                action_html = (
                    f'<div class="chat-bubble-action">'
                    f'<b>📌 Request:</b> {m["action_type"].upper()} '
                    f'CRN {int(m["action_crn"])} &nbsp;·&nbsp; {status}'
                    f'</div>'
                )

            bubbles.append(
                f'<div style="text-align:{align}">'
                f'  <div class="{bubble_cls}">'
                f'    <div class="chat-bubble-meta">'
                f'      {sender_name_msg} &nbsp;·&nbsp; {ts}'
                f'    </div>'
                f'    <div class="chat-bubble-body">{body}</div>'
                f'    {action_html}'
                f'  </div>'
                f'</div>'
            )
    bubbles.append('</div>')
    st.markdown("".join(bubbles), unsafe_allow_html=True)

    # Compose
    body = st.text_area(
        "Message",
        key=body_key,
        placeholder="Type your message to your advisor…",
        label_visibility="collapsed",
        height=80,
    )
    col_send, col_full = st.columns([1, 1])
    with col_send:
        if st.button("📤 Send", key=f"_fab_send_{sid}",
                     type="primary", use_container_width=True):
            if not body.strip():
                st.warning("Message cannot be empty.")
            else:
                ok = send_message(
                    "student", int(advisor_id), int(sid), body.strip(),
                )
                if ok:
                    st.session_state[f"_clear_{body_key}"] = True
                    st.rerun()
                else:
                    st.error("❌ Could not send message.")
    with col_full:
        if st.button("📨 Open full chat", key=f"_fab_full_{sid}",
                     use_container_width=True):
            st.session_state.page = "student_chat"
            st.rerun()


def render_advisor_fab() -> None:
    """
    Render a floating action button (bottom-right) that opens a popup chat
    dialog with the student's assigned academic advisor. Safe to call at the
    end of any student-facing page.
    """
    import streamlit as st
    from db.advisor import get_student_advisor

    sid = st.session_state.get("student_id")
    if not sid:
        return

    advisor_id = get_student_advisor(int(sid))
    if advisor_id is None:
        return  # nothing to chat with

    advisor_name = st.session_state.get("student_info", {}).get(
        "advisor_name", "Academic Advisor"
    )
    student_name = st.session_state.get("student_name", "Student")

    # Tooltip badge (CSS-positioned, decorative)
    st.markdown(
        '<div class="uoh-fab-tag">💬 Chat with your Advisor</div>',
        unsafe_allow_html=True,
    )

    # Floating wrapper container — CSS in styles.py pins it bottom-right
    with st.container(key="uoh_advisor_fab_wrap"):
        clicked = st.button(
            "💬", key="uoh_advisor_fab_btn",
            help="Chat with your Academic Advisor",
        )

    if clicked:
        @st.dialog("💬 Academic Advisor Chat", width="large")
        def _advisor_chat_dialog():
            _render_chat_dialog_body(
                int(advisor_id), int(sid), student_name, advisor_name,
            )

        _advisor_chat_dialog()
