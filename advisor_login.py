"""
ui/pages/advisor_login.py — Academic Advisor login page.

Mirrors the split two-panel card layout used by `ui/pages/login.py` so the
visual design and CSS classes stay 100% reused — no new styles introduced.
"""

import streamlit as st
import pandas as pd

from db.advisor import authenticate_advisor
from ui.components import nav
from ui.styles import LOGO


def page_advisor_login() -> None:
    nav()
    st.markdown("<div style='height:36px'></div>", unsafe_allow_html=True)

    _, col_l, col_r, _ = st.columns([0.8, 1.2, 1.6, 0.8])

    # ── Left: branding panel (same shell as student login) ───────────────────
    with col_l:
        st.markdown(f"""
<div class="login-left">
  <img src="{LOGO}" alt="UoH Logo">
  <h2>University of Hail</h2>
  <p>Academic Advisor Portal<br>Guide your students with AI-assisted advising</p>
  <div>
    <span class="l-badge">👩‍🏫 Advisor Console</span><br>
    <span class="l-badge">📋 Schedules</span><br>
    <span class="l-badge">💬 Student Chat</span>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Right: advisor login form ────────────────────────────────────────────
    with col_r:
        st.markdown("""
<h3 style="color:#0b1e48;font-size:1.3rem;font-weight:900;margin:0 0 4px">
  🎓 Advisor Login</h3>
<p style="color:#64748b;font-size:.8rem;margin:0 0 22px">
  Sign in with your advisor credentials to manage your students.</p>
""", unsafe_allow_html=True)

        with st.form("advisor_login_form"):
            aid = st.text_input("Advisor ID", placeholder="e.g. 1001")
            pwd = st.text_input("Password",   placeholder="Enter your password",
                                type="password")
            submitted = st.form_submit_button(
                "🔑 Sign In", use_container_width=True, type="primary"
            )

        if submitted:
            _handle_advisor_login(aid, pwd)

        with st.expander("ℹ️ Demo Advisor Accounts"):
            st.dataframe(
                pd.DataFrame({
                    "Advisor ID": ["1001", "1002"],
                    "Password":   ["Sara@1001", "Nora@1002"],
                }),
                hide_index=True,
                width="stretch",
            )

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        if st.button("← Back to Student Login", key="back_to_student_login"):
            st.session_state.advisor_mode = False
            st.rerun()


def _handle_advisor_login(aid: str, pwd: str) -> None:
    if not str(aid).strip() or not str(pwd).strip():
        st.error("Please enter both Advisor ID and password.")
        return

    advisor = authenticate_advisor(aid.strip(), pwd.strip())
    if advisor:
        st.session_state.update({
            "advisor_logged_in":   True,
            "advisor_id":          int(advisor["id"]),
            "advisor_name":        advisor.get("name", str(advisor["id"])),
            "advisor_page":        "advisor_home",
            "selected_student_id": None,
            "advisor_mode":        False,
        })
        st.rerun()
    else:
        st.error("❌ Invalid advisor credentials.")
