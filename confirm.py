"""
ui/pages/confirm.py — Confirmation page before committing a Change or Add.
Shows a summary card → Confirm saves to DB → Cancel goes back.
"""

import streamlit as st

from db.advisor import get_student_advisor, send_message
from engine.time_utils import DAY_NAMES
from ui.components import nav, breadcrumb, sec_title, hr, info


def page_confirm() -> None:
    sid  = st.session_state.student_id
    name = st.session_state.student_name
    crn  = st.session_state.confirm_crn
    mode = st.session_state.confirm_mode
    data = st.session_state.confirm_data or {}
    old  = st.session_state.confirm_old  or []

    prev_page  = "change" if mode == "change" else "add"
    prev_label = "🔄 Change Section" if mode == "change" else "➕ Add Course"
    verb       = "Change to" if mode == "change" else "Add"
    action     = "changed to" if mode == "change" else "added"
    score      = int(data.get("Score", 3))
    day        = data.get(
        "Day_name",
        DAY_NAMES.get(str(data.get("Days", "")), str(data.get("Days", ""))),
    )

    nav(f'<span class="uoh-nav-pill"><b>{name}</b> &nbsp;·&nbsp; {sid}</span>')
    breadcrumb([("🏠 Home", "home"), (prev_label, prev_page), ("✅ Confirm", None)])

    sec_title("✅", "Confirm Your Selection",
              "Please review the details carefully before confirming")

    # ── Confirmation card (static HTML) ──────────────────────────────────────
    old_row_html = ""
    if old:
        old_row_html = (
            f'<div><div class="cf-label">Replaces CRN(s)</div>'
            f'<div class="cf-value">{" / ".join(str(c) for c in old)}</div></div>'
        )

    st.markdown(f"""
<div class="confirm-card">
  <h3>⚠️ {verb} — CRN {crn}</h3>
  <div class="cf-grid">
    <div>
      <div class="cf-label">Course</div>
      <div class="cf-value">{data.get('Code','')} &mdash; {data.get('Course_name','')}</div>
    </div>
    <div>
      <div class="cf-label">Day</div>
      <div class="cf-value">{day}</div>
    </div>
    <div>
      <div class="cf-label">Time</div>
      <div class="cf-value">{data.get('STime','—')} – {data.get('ETim','—')}</div>
    </div>
    <div>
      <div class="cf-label">Location</div>
      <div class="cf-value">{data.get('Location','—')}</div>
    </div>
    <div>
      <div class="cf-label">Instructor</div>
      <div class="cf-value">{data.get('Instructor','—')}</div>
    </div>
    <div>
      <div class="cf-label">Open Seats</div>
      <div class="cf-value">{data.get('Seats','—')}</div>
    </div>
    <div>
      <div class="cf-label">AI Score</div>
      <div class="cf-value">{"⭐" * score} ({score}/5)</div>
    </div>
    {old_row_html}
  </div>
</div>
""", unsafe_allow_html=True)

    info(
        "This request will be sent to your academic advisor for review and approval. "
        "Your current schedule will not change until the advisor approves the request."
    )

    # ── Action buttons (native Streamlit) ─────────────────────────────────────
    c1, c2, _ = st.columns([1.2, 1.2, 5])
    with c1:
        if st.button("📤 Submit Request", use_container_width=True, type="primary"):
            _commit(sid, mode, old, crn, action, data, day)

    with c2:
        if st.button("✖ Cancel", use_container_width=True):
            _clear_confirm()
            st.session_state.page = prev_page
            st.rerun()

    hr()


def _commit(sid, mode, old, crn, action, data, day):
    advisor_id = get_student_advisor(int(sid))
    if advisor_id is None:
        st.error("❌ No academic advisor is assigned to your account. Cannot submit request.")
        return

    course_label = (
        f"{data.get('Code','')} — {data.get('Course_name','')} "
        f"({day} {data.get('STime','')}–{data.get('ETim','')})"
    )

    if mode == "change":
        old_str = ", ".join(str(c) for c in old)
        body = (
            f"Section change request: drop CRN {old_str}, add CRN {crn} "
            f"({course_label})"
        )
        ok = send_message(
            "student", int(advisor_id), int(sid),
            body,
            action_type="change",
            action_crn=int(crn),
            action_old_crns=[int(c) for c in old],
        )
    else:
        body = f"Add course request: CRN {crn} ({course_label})"
        ok = send_message(
            "student", int(advisor_id), int(sid),
            body,
            action_type="add",
            action_crn=int(crn),
        )

    if ok:
        st.session_state.success_msg = (
            "⏳ Your request has been submitted successfully and is pending advisor approval."
        )
        _clear_confirm()
        st.session_state.page = "home"
        st.rerun()
        return

    st.error("❌ Could not submit request — please try again.")


def _clear_confirm():
    for k in ("confirm_crn", "confirm_mode", "confirm_old", "confirm_data"):
        st.session_state[k] = None
