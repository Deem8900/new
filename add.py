"""
ui/pages/add.py — Add Course page.

Flow:
  Step 1 — Student picks a course not yet in their schedule.
  Step 2 — Pre-flight policy check: hours cap + prerequisites + duplicate.
  Step 3 — Algorithm (IntervalTree + scoring) returns top-3 sections,
           plus an explanatory note listing the OTHER sections that
           were filtered out and why (time conflict, day conflict,
           full capacity, or duplicate course).
  Student selects one → navigate to confirm page.
"""

import streamlit as st

from db.queries import (
    get_addable_courses,
    get_available_sections_to_add_detailed,
    check_add_eligibility,
)
from ui.components import nav, breadcrumb, sec_title, info, warn, hr, section_card

# Friendly label per rejection reason code
_REASON_LABELS = {
    "time_conflict":     "⏰ Time conflict",
    "no_seats":          "💺 Full — no seats",
    "duplicate_course":  "🔁 Already in this course",
}


def page_add() -> None:
    sid  = st.session_state.student_id
    name = st.session_state.student_name

    nav(f'<span class="uoh-nav-pill"><b>{name}</b> &nbsp;·&nbsp; {sid}</span>')
    breadcrumb([("🏠 Home", "home"), ("➕ Add Course", None)])

    sec_title("➕", "Add New Course",
              "Enroll in a course not currently in your schedule")

    if st.button("← Back to Schedule"):
        st.session_state.page = "home"
        st.rerun()

    hr()

    # ── Step 1: Pick new course ───────────────────────────────────────────────
    sec_title("📚", "Step 1 — Select Course to Add",
              "Courses available for enrollment")

    with st.spinner("Loading available courses…"):
        addable = get_addable_courses(sid)

    if not addable:
        warn("You are already enrolled in all available courses.")
        return

    options = ["— Select a course to add —"] + [
        f"{c['code']} — {c['course_name']}  ({c['hours']} cr)"
        for c in addable
    ]
    sel = st.selectbox("select_course_add", options, label_visibility="collapsed")

    if sel == "— Select a course to add —":
        info("Choose a course you would like to enroll in.")
        return

    add_code = sel.split(" — ")[0].strip()
    hr()

    # ── Step 2: Pre-flight eligibility check ─────────────────────────────────
    sec_title("🛡️", "Step 2 — Eligibility Check",
              "Hours, prerequisites, and duplicate-course guard")

    check = check_add_eligibility(int(sid), add_code)
    _render_eligibility_panel(check)

    if not check["ok"]:
        warn(
            "This course cannot be added until the issue(s) above are "
            "resolved. Please pick a different course."
        )
        return

    hr()

    # ── Step 3: Algorithm → top 3 sections + rejection notes ────────────────
    sec_title("⭐", "Step 3 — Best Available Sections",
              "AI-ranked top 3 conflict-free sections")

    with st.spinner("⏳ Running conflict detection and scoring…"):
        secs_df, rejected = get_available_sections_to_add_detailed(sid, add_code)

    if secs_df.empty:
        warn("No conflict-free sections available — all sections overlap with your schedule "
             "or are fully booked.")
        if rejected:
            _render_rejected_panel(rejected, add_code)
        return

    top3 = secs_df.head(3)
    info(
        f"Found <b>{len(secs_df)}</b> conflict-free section(s) for "
        f"<b>{add_code}</b> — showing the top <b>{len(top3)}</b> by AI score."
    )

    cards_container = st.container()
    with cards_container:
        for rank, (_, row) in enumerate(top3.iterrows()):
            row_dict = row.to_dict()
            is_fallback = bool(row_dict.get("fallback", False))
            btn_label   = "⚠️ Join Waitlist" if is_fallback else "➕ Add this section"
            if section_card(
                row_dict, rank,
                btn_label=btn_label,
                key=f"add_{int(row['Cec'])}_{rank}",
            ):
                st.session_state.update({
                    "confirm_crn":  int(row["Cec"]),
                    "confirm_mode": "add",
                    "confirm_old":  [],
                    "confirm_data": row_dict,
                    "page":         "confirm",
                })
                st.rerun()

    # Notes — explain why the OTHER sections were not chosen
    if rejected:
        hr()
        _render_rejected_panel(rejected, add_code)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _render_eligibility_panel(check: dict) -> None:
    """Show the student their hour load, prereqs, and any blocking reasons."""
    cur     = int(check.get("current_hours") or 0)
    add_h   = int(check.get("course_hours") or 0)
    proj    = int(check.get("projected_hours") or 0)
    cap     = int(check.get("max_hours") or 0)
    prereqs = check.get("prereqs") or []
    miss    = check.get("missing_prereqs") or []

    prereq_html = (
        "None"
        if not prereqs
        else ", ".join(
            f"<span style='color:#ef4444'><b>{p}</b> ❌</span>"
            if p in miss
            else f"<span style='color:#22c55e'>{p} ✅</span>"
            for p in prereqs
        )
    )

    st.markdown(
        f"""
<div class="box-info">
  <div><b>📚 Current load:</b> {cur} h &nbsp;·&nbsp;
       <b>➕ Course hours:</b> {add_h} h &nbsp;·&nbsp;
       <b>🎯 After adding:</b> {proj} h / {cap} h cap</div>
  <div style="margin-top:6px"><b>📋 Prerequisites:</b> {prereq_html}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    for r in check.get("reasons", []):
        warn(r)
    for w in check.get("warnings", []):
        info(w)


def _render_rejected_panel(rejected: list[dict], course_code: str) -> None:
    """List the sections that were NOT chosen along with the reason."""
    sec_title(
        "📝",
        "Why other sections were not chosen",
        f"Notes on the remaining {course_code} sections that were filtered out",
    )

    rows_html = ""
    for r in rejected:
        label = _REASON_LABELS.get(r.get("reason_code", ""), "ℹ️ Filtered")
        day   = r.get("Day_name") or r.get("Days") or "—"
        rows_html += (
            "<tr>"
            f"<td><b>{r.get('Cec','—')}</b></td>"
            f"<td>{day}</td>"
            f"<td>{r.get('STime','—')} – {r.get('ETim','—')}</td>"
            f"<td>{r.get('Instructor','—')}</td>"
            f"<td>{r.get('Seats','—')}</td>"
            f"<td><b>{label}</b><br>"
            f"<span style='font-size:.78rem;color:#94a3b8'>{r.get('reason','')}</span></td>"
            "</tr>"
        )

    st.markdown(
        f"""
<div class="sched-wrap">
  <table class="sched-tbl">
    <thead><tr>
      <th>Ref No.</th><th>Day</th><th>Time</th>
      <th>Instructor</th><th>Open Seats</th><th>Reason</th>
    </tr></thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>
""",
        unsafe_allow_html=True,
    )
