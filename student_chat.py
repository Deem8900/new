"""
ui/pages/student_chat.py — Student-side messaging page.

Lets a student message their assigned academic advisor. The student can attach
an optional course-action request (add / drop a CRN) which the advisor can
execute from their own view.
"""

import streamlit as st

from db.advisor    import get_student_advisor, get_messages, send_message
from ui.components import (
    nav, sec_title, hr,
    render_chat_bubble, render_chat_empty_state, warn,
)


def page_student_chat() -> None:
    sid  = st.session_state.student_id
    name = st.session_state.student_name

    nav(f'<span class="uoh-nav-pill"><b>{name}</b> &nbsp;·&nbsp; {sid}</span>')

    sec_title("💬", "Message Your Academic Advisor",
              "Ask questions or request a course action")

    if st.button("← Back to Schedule", key="back_from_chat"):
        st.session_state.page = "home"
        st.rerun()
        return

    advisor_id = get_student_advisor(int(sid))
    if advisor_id is None:
        warn("No academic advisor is assigned to you yet.")
        return

    # Pending-clear flag MUST be honoured before the text-area widget is
    # instantiated, otherwise Streamlit raises StreamlitAPIException when we
    # try to reset the field after sending.
    body_key = f"student_chat_body_{sid}"
    if st.session_state.pop(f"_clear_{body_key}", False):
        st.session_state[body_key] = ""

    msgs = get_messages(int(advisor_id), int(sid))

    # ── Chat scroll area with enhanced bubbles ────────────────────────────────
    st.markdown('<div class="uoh-chat-scroll">', unsafe_allow_html=True)
    if not msgs:
        render_chat_empty_state()
    else:
        for m in msgs:
            render_chat_bubble(m, viewer_role="student")
    st.markdown('</div>', unsafe_allow_html=True)

    hr()

    # ── Compose form ─────────────────────────────────────────────────────────
    sec_title("✍️", "Send a Message", "Write your message to your advisor")

    body = st.text_area(
        "Message",
        key=body_key,
        placeholder="Type your message to your advisor here…",
    )

    col_send, _ = st.columns([1, 4])
    if col_send.button("📤 Send", key=f"student_chat_send_{sid}",
                       type="primary", use_container_width=True):
        if not body.strip():
            st.warning("Message cannot be empty.")
        else:
            ok = send_message(
                "student", int(advisor_id), int(sid),
                body.strip(),
            )
            if ok:
                st.session_state[f"_clear_{body_key}"] = True
                st.rerun()
            else:
                st.error("❌ Could not send message.")
