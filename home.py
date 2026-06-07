"""
ui/pages/home.py — Home / dashboard page.
Shows the student schedule table, notification panel,
and the service action buttons (Change / Add / Message).
"""

import streamlit as st

from db.queries import load_student_schedule
from ui.components import nav, sec_title, schedule_table, hr, render_notification_panel


def page_home() -> None:
    sid  = st.session_state.student_id
    name = st.session_state.student_name
    info = st.session_state.student_info

    nav(f'<span class="uoh-nav-pill"><b>{name}</b> &nbsp;·&nbsp; {sid}</span>')

    # ── Welcome strip ─────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="uoh-welcome">
  <div>
    <h2>👩‍🎓 Welcome back, {name}!</h2>
    <p>Academic Advising Portal &nbsp;·&nbsp; Spring Semester 2024–2025</p>
  </div>
  <div>
    <span class="uoh-badge">🎓 {info.get('specialization','Computer Science')}</span>
    <span class="uoh-badge">📊 Level {info.get('level','2')}</span>
    <span class="uoh-badge">🆔 {sid}</span>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Success banner ────────────────────────────────────────────────────────
    if st.session_state.success_msg:
        st.success(st.session_state.success_msg)
        st.session_state.success_msg = None

    # ── Notifications ─────────────────────────────────────────────────────────
    render_notification_panel("student", int(sid))

    # ── Schedule table ────────────────────────────────────────────────────────
    sec_title("📋", "Your Current Schedule",
              "Registered sections for this semester")
    df = load_student_schedule(sid)
    schedule_table(df)

    hr()

    # ── Service buttons (small, arranged neatly) ──────────────────────────────
    sec_title("🔧", "Academic Services", "What would you like to do today?")

    col_ch, col_ad, col_msg, _ = st.columns([1, 1, 1, 2])
    with col_ch:
        if st.button("🔄 Change Section", use_container_width=True, type="primary"):
            st.session_state.page = "change"
            st.session_state.change_course = None
            st.rerun()
    with col_ad:
        if st.button("➕ Add Course", use_container_width=True):
            st.session_state.page = "add"
            st.rerun()
    with col_msg:
        if st.button("💬 Message Advisor", use_container_width=True):
            st.session_state.page = "student_chat"
            st.rerun()

    hr()
    if st.button("🚪 Logout", key="logout_home"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
