"""
streamlit_app.py — AcademiQ entry point.

Responsibilities (only):
  1. st.set_page_config — must be the very first Streamlit call.
  2. Initialise session state defaults.
  3. Inject global CSS.
  4. Auto-create the notifications table if missing.
  5. Route to the correct page based on st.session_state.page.
"""

import streamlit as st

from ui.styles import load_css
from ui.pages.login           import page_login
from ui.pages.home            import page_home
from ui.pages.change          import page_change
from ui.pages.add             import page_add
from ui.pages.confirm         import page_confirm
from ui.pages.advisor_login   import page_advisor_login
from ui.pages.advisor_home    import page_advisor_home
from ui.pages.advisor_student import page_advisor_student
from ui.pages.student_chat    import page_student_chat

# ── 1. Page configuration (must come before any other Streamlit call) ─────────
st.set_page_config(
    page_title="AcademiQ — University of Hail",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── 2. Session state defaults ─────────────────────────────────────────────────
DEFAULTS: dict = dict(
    logged_in=False,
    student_id=None,
    student_name=None,
    student_info={},
    page="home",            # home | change | add | confirm | student_chat
    change_course=None,
    confirm_crn=None,
    confirm_mode=None,
    confirm_old=None,
    confirm_data=None,
    success_msg=None,
    advisor_logged_in=False,
    advisor_id=None,
    advisor_name=None,
    advisor_page="advisor_home",
    selected_student_id=None,
    advisor_mode=False,
)
for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── 3. Global CSS ─────────────────────────────────────────────────────────────
load_css()

# ── 4. Auto-create/migrate DB tables if needed ────────────────────────────────
if not st.session_state.get("_notif_table_checked"):
    try:
        from db.connection import ensure_notifications_table
        ensure_notifications_table()
        st.session_state["_notif_table_checked"] = True
    except Exception:
        pass  # DB might not be configured yet (login page will show first)

if not st.session_state.get("_msg_migration_checked"):
    try:
        from db.advisor import ensure_action_old_crns_column
        ensure_action_old_crns_column()
        st.session_state["_msg_migration_checked"] = True
    except Exception:
        pass

# ── 5. Page router ────────────────────────────────────────────────────────────
if st.session_state.get("advisor_logged_in"):
    adv_page = st.session_state.get("advisor_page", "advisor_home")
    if   adv_page == "advisor_home":    page_advisor_home()
    elif adv_page == "advisor_student": page_advisor_student()
    else:
        st.session_state.advisor_page = "advisor_home"
        st.rerun()
    st.stop()

if st.session_state.get("advisor_mode"):
    page_advisor_login()
    st.stop()

if not st.session_state.logged_in:
    page_login(DEFAULTS)
else:
    page = st.session_state.get("page", "home")
    if   page == "home":         page_home()
    elif page == "change":       page_change()
    elif page == "add":          page_add()
    elif page == "confirm":      page_confirm()
    elif page == "student_chat": page_student_chat()
    else:
        st.session_state.page = "home"
        st.rerun()

    # Floating "Chat with Advisor" widget — visible on all student pages
    # except the dedicated chat page (avoids a duplicate chat surface).
    if page != "student_chat":
        from ui.components import render_advisor_fab
        render_advisor_fab()
