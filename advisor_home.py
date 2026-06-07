"""
ui/pages/advisor_home.py — Advisor dashboard listing assigned students.

Per supervisor request:
  * On advisor login, show 2-3 assigned students in a TABLE (id + name)
    rather than as cards.
  * The advisor's primary job is to APPROVE schedule changes a student
    has requested (section change or new course). The "Pending requests"
    column highlights students who currently need approval.
"""

import html as _html
import streamlit as st

from db.advisor import get_advisor_students, get_messages
from ui.components import nav, sec_title, hr, info, warn, render_notification_panel


def page_advisor_home() -> None:
    aid  = st.session_state.advisor_id
    name = st.session_state.advisor_name

    nav(f'<span class="uoh-nav-pill"><b>{name}</b> &nbsp;·&nbsp; Advisor</span>')

    # ── Welcome strip for advisor ─────────────────────────────────────────────
    st.markdown(f"""
<div class="uoh-welcome">
  <div>
    <h2>👩‍🏫 Welcome back, {name}!</h2>
    <p>Academic Advisor Portal &nbsp;·&nbsp; Approve student schedule changes</p>
  </div>
  <div>
    <span class="uoh-badge">🎓 Advisor Console</span>
    <span class="uoh-badge">🆔 {aid}</span>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Notifications ─────────────────────────────────────────────────────────
    render_notification_panel("advisor", int(aid))

    sec_title("👩‍🏫", "Your Assigned Students",
              "Approve a student's schedule when they change a section "
              "or add a course")

    students = get_advisor_students(int(aid))
    if not students:
        warn("No students are currently assigned to you.")
        hr()
        if st.button("🚪 Logout", key="logout_advisor_empty"):
            _clear_advisor_session()
        return

    info(
        f"You have <b>{len(students)}</b> assigned student(s). "
        f"Select <b>Review &amp; Approve</b> on any row to view their "
        f"pending request and approve the change."
    )

    # ── Build the table (2-3 students, id + name + status + action) ──────────
    rows_html = ""
    for stu in students:
        sid        = stu["student_id"]
        stu_name   = _html.escape(stu.get("name") or str(sid))
        speciality = _html.escape(str(stu.get("specialization") or "—"))
        level      = _html.escape(str(stu.get("level") or "—"))
        pending    = _count_pending_requests(int(aid), int(sid))

        if pending > 0:
            status_html = (
                f'<span class="notif-badge">{pending} pending</span>'
            )
        else:
            status_html = (
                '<span style="color:#22c55e">✅ Up to date</span>'
            )

        rows_html += (
            "<tr>"
            f"<td class='ref-col'>{sid}</td>"
            f"<td style='text-align:left'><b>{stu_name}</b></td>"
            f"<td>{speciality}</td>"
            f"<td>Level {level}</td>"
            f"<td>{status_html}</td>"
            "</tr>"
        )

    st.markdown(
        f"""
<div class="sched-wrap">
  <table class="sched-tbl">
    <thead><tr>
      <th>Student ID</th>
      <th>Name</th>
      <th>Specialisation</th>
      <th>Level</th>
      <th>Approval Status</th>
    </tr></thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # ── Action buttons row (one per student, aligned with the table) ─────────
    sec_title("✅", "Review & Approve",
              "Open a student's file to approve their pending request")
    for stu in students:
        sid      = stu["student_id"]
        stu_name = _html.escape(stu.get("name") or str(sid))
        pending  = _count_pending_requests(int(aid), int(sid))
        label_extra = f" — {pending} pending" if pending else ""

        if st.button(
            f"📋 Review {stu_name} (ID {sid}){label_extra}",
            key=f"view_student_{sid}",
            use_container_width=True,
            type="primary" if pending else "secondary",
        ):
            st.session_state.selected_student_id = int(sid)
            st.session_state.advisor_page        = "advisor_student"
            st.rerun()

    hr()
    if st.button("🚪 Logout", key="logout_advisor_home"):
        _clear_advisor_session()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _count_pending_requests(advisor_id: int, student_id: int) -> int:
    """
    Number of student messages still awaiting advisor approval.
    A "pending request" is a message authored by the student that carries
    an action_type (add / drop / change) and has not been handled yet.
    """
    try:
        msgs = get_messages(advisor_id, student_id)
    except Exception:
        return 0
    return sum(
        1 for m in msgs
        if str(m.get("sender_role", "")).lower() == "student"
        and m.get("action_type")
        and not int(m.get("handled") or 0)
    )


def _clear_advisor_session() -> None:
    """Clear every advisor_* key from session state and rerun."""
    for k in list(st.session_state.keys()):
        if str(k).startswith("advisor_") or k == "selected_student_id":
            del st.session_state[k]
    st.rerun()
