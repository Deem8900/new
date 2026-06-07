"""
ui/pages/advisor_student.py — Advisor's student detail view.

Two tabs:
  1) Schedule & Requests — shows the student's current schedule and any pending
     requests, each with old-schedule / proposed-new-schedule preview and
     Approve / Reject buttons.
  2) Chat — read and reply to the student's messages.

The advisor cannot directly add or drop courses for a student; all changes
must go through the student-submitted request workflow.
"""

import streamlit as st

from db.queries  import load_student_schedule, build_proposed_schedule
from db.writes   import do_change_section, do_add_section
from db.advisor  import (
    get_messages, send_message, mark_request_handled,
    reject_request, get_pending_requests,
)
from ui.components import (
    nav, sec_title, schedule_table, hr, info, warn,
    render_chat_bubble, render_chat_empty_state,
)


def _unwrap_add_result(result) -> tuple[bool, list[str]]:
    if isinstance(result, tuple):
        ok, reasons = result
        return bool(ok), list(reasons or [])
    return bool(result), []


def page_advisor_student() -> None:
    aid = st.session_state.advisor_id
    sid = st.session_state.selected_student_id
    adv_name = st.session_state.advisor_name

    if sid is None:
        st.session_state.advisor_page = "advisor_home"
        st.rerun()
        return

    nav(f'<span class="uoh-nav-pill"><b>{adv_name}</b> &nbsp;·&nbsp; Advisor</span>')

    sec_title("👤", f"Student #{sid}",
              "View schedule, approve pending requests, and chat")

    if st.button("← Back to Students", key="back_to_advisor_home"):
        st.session_state.advisor_page = "advisor_home"
        st.rerun()
        return

    tab_sched, tab_chat = st.tabs(
        ["📋 Schedule & Requests", "💬 Chat"]
    )

    with tab_sched:
        _render_schedule_tab(int(aid), int(sid))

    with tab_chat:
        _render_chat_tab(int(aid), int(sid))


# ── Tab 1 ─────────────────────────────────────────────────────────────────────

def _render_schedule_tab(aid: int, sid: int) -> None:
    current_df = load_student_schedule(sid)

    sec_title("📋", "Current Schedule", "Sections currently registered by this student")
    schedule_table(current_df)

    if current_df.empty:
        warn("This student has no registered courses yet.")
    else:
        info(
            f"This student is registered in <b>{len(current_df)}</b> section row(s). "
            f"Changes are applied only after the advisor approves a student request."
        )

    pending = get_pending_requests(aid, sid)
    if not pending:
        return

    hr()
    sec_title("⏳", "Pending Requests",
              "Review each request — approve to apply the change, or reject to dismiss it")

    for req in pending:
        _render_pending_request_card(aid, sid, req, current_df)


def _render_pending_request_card(
    aid: int, sid: int, req: dict, current_df
) -> None:
    action_type   = str(req.get("action_type") or "")
    action_crn    = req.get("action_crn")
    old_crns_raw  = req.get("action_old_crns") or ""
    msg_id        = int(req["id"])
    body          = req.get("body", "")

    old_crns: list[int] = []
    if old_crns_raw:
        try:
            old_crns = [int(x.strip()) for x in str(old_crns_raw).split(",") if x.strip()]
        except ValueError:
            old_crns = []

    if action_type == "change":
        label = f"🔄 Section Change Request — Add CRN {action_crn}"
    elif action_type == "add":
        label = f"➕ Add Course Request — CRN {action_crn}"
    else:
        label = f"📝 Request ({action_type}) — CRN {action_crn}"

    with st.expander(label, expanded=True):
        st.markdown(f"**Student message:** {body}")
        st.markdown("---")

        col_old, col_new = st.columns(2)

        with col_old:
            st.markdown("#### 📋 Current Schedule")
            schedule_table(current_df)

        with col_new:
            st.markdown("#### 🆕 Proposed Schedule (if approved)")
            if action_crn is not None:
                proposed_df = build_proposed_schedule(
                    current_df, action_type, int(action_crn), old_crns
                )
                schedule_table(proposed_df)
            else:
                warn("Cannot preview proposed schedule — CRN is missing.")

        st.markdown("---")
        col_approve, col_reject, _ = st.columns([1, 1, 4])
        with col_approve:
            if st.button("✅ Approve", key=f"approve_{msg_id}",
                         type="primary", use_container_width=True):
                _execute_request(aid, sid, msg_id, action_type,
                                 int(action_crn) if action_crn else 0, old_crns)
        with col_reject:
            if st.button("❌ Reject", key=f"reject_{msg_id}",
                         use_container_width=True):
                _reject_request(aid, sid, msg_id,
                                action_type,
                                int(action_crn) if action_crn else 0)


# ── Tab 2 ─────────────────────────────────────────────────────────────────────

def _render_chat_tab(aid: int, sid: int) -> None:
    sec_title("💬", "Chat with Student",
              "View the full message history and send replies")

    body_key = f"advisor_reply_body_{sid}"
    if st.session_state.pop(f"_clear_{body_key}", False):
        st.session_state[body_key] = ""

    msgs = get_messages(aid, sid)

    st.markdown('<div class="uoh-chat-scroll">', unsafe_allow_html=True)
    if not msgs:
        render_chat_empty_state()
    else:
        for m in msgs:
            render_chat_bubble(m, viewer_role="advisor")
    st.markdown('</div>', unsafe_allow_html=True)

    hr()

    sec_title("✍️", "Send Reply", "Compose a message to this student")
    body = st.text_area(
        "Reply",
        key=body_key,
        placeholder="Type your message here…",
        label_visibility="collapsed",
    )
    col_send, _ = st.columns([1, 4])
    if col_send.button("📤 Send Reply", key=f"advisor_send_{sid}",
                       type="primary", use_container_width=True):
        if not body.strip():
            st.warning("Message cannot be empty.")
        else:
            ok = send_message("advisor", aid, sid, body.strip())
            if ok:
                st.session_state[f"_clear_{body_key}"] = True
                st.rerun()
            else:
                st.error("❌ Could not send message.")


# ── Request execution helpers ─────────────────────────────────────────────────

def _execute_request(
    aid: int, sid: int, msg_id: int,
    action_type: str, action_crn: int, old_crns: list[int],
) -> None:
    from db.queries import get_section_as_schedule_row

    if action_crn == 0 or get_section_as_schedule_row(action_crn) is None:
        st.error(
            f"❌ Cannot execute request — CRN {action_crn} does not exist in the system. "
            f"Please reject this request."
        )
        return

    reasons: list[str] = []

    if action_type == "change":
        ok = do_change_section(sid, old_crns, action_crn)
    elif action_type == "add":
        ok, reasons = _unwrap_add_result(do_add_section(sid, action_crn))
    else:
        ok = False
        reasons = [f"Unknown request type: {action_type}"]

    if not ok:
        msg = f"❌ Could not execute request (CRN {action_crn} for student {sid})."
        if reasons:
            msg += "\n\n• " + "\n• ".join(reasons)
        st.error(msg)
        return

    mark_request_handled(msg_id)
    verb = "change" if action_type == "change" else "addition of"
    send_message(
        "advisor", aid, sid,
        f"✅ Your request to {verb} CRN {action_crn} has been approved and applied to your schedule.",
    )
    st.rerun()


def _reject_request(
    aid: int, sid: int, msg_id: int,
    action_type: str, action_crn: int,
) -> None:
    reject_request(msg_id)
    verb = "section change" if action_type == "change" else "course addition"
    send_message(
        "advisor", aid, sid,
        f"❌ Your {verb} request for CRN {action_crn} has been rejected. "
        f"Please contact your advisor for more details.",
    )
    st.rerun()
