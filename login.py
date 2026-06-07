"""
ui/pages/login.py — Login page (split two-panel card layout).
"""

import streamlit as st

from db.auth import authenticate
from ui.components import nav
from ui.styles import LOGO


def page_login(defaults: dict) -> None:
    nav()
    st.markdown("<div style='height:36px'></div>", unsafe_allow_html=True)

    _, col_l, col_r, _ = st.columns([0.8, 1.2, 1.6, 0.8])

    # ── Left: branding panel (static HTML) ───────────────────────────────────
    with col_l:
        st.markdown(f"""
<div class="login-left">
  <img src="{LOGO}" alt="UoH Logo">
  <h2>University of Hail</h2>
  <p>Smart Academic Advising System<br>Build your perfect schedule with AI</p>
  <div>
    <span class="l-badge">🎓 Academic Advising</span><br>
    <span class="l-badge">🤖 AI Powered</span><br>
    <span class="l-badge">🔍 Conflict Detection</span>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Right: login form (native Streamlit) ──────────────────────────────────
    with col_r:
        st.markdown("""
<h3 style="color:#0b1e48;font-size:1.3rem;font-weight:900;margin:0 0 4px">
  🔐 Student Login</h3>
<p style="color:#64748b;font-size:.8rem;margin:0 0 22px">
  Sign in with your university credentials to continue.</p>
""", unsafe_allow_html=True)

        with st.form("login_form"):
            uid = st.text_input("Student ID", placeholder="e.g. 20240018")
            pwd = st.text_input("Password",   placeholder="Enter your password",
                                type="password")
            submitted = st.form_submit_button(
                "🔑 Sign In", use_container_width=True, type="primary"
            )

        if submitted:
            _handle_login(uid, pwd, defaults)

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if st.button("🎓 Academic Advisor? Login here",
                     key="goto_advisor_login",
                     use_container_width=True):
            st.session_state.advisor_mode = True
            st.rerun()


def _handle_login(uid: str, pwd: str, defaults: dict) -> None:
    if not uid.strip() or not pwd.strip():
        st.error("Please enter both Student ID and password.")
        return

    student = authenticate(uid.strip(), pwd.strip())
    if student:
        for k in defaults:
            st.session_state[k] = defaults[k]
        st.session_state.update({
            "logged_in":    True,
            "student_id":   student["id"],
            "student_name": student.get("name", str(student["id"])),
            "student_info": student,
        })
        st.rerun()
    else:
        st.error("❌ Invalid credentials. Please try again.")
