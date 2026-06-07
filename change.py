"""
ui/pages/change.py — Change Section page.

Flow:
  Step 1 — Student picks which enrolled course to swap.
  Step 2 — Algorithm (IntervalTree + scoring) returns top-3 sections,
           plus an explanatory note listing the OTHER sections that
           were filtered out and why (time conflict or full capacity).
  Student selects one → navigate to confirm page.
"""

import streamlit as st

from db.queries import load_student_schedule, get_available_alternatives
from engine.time_utils import DAY_NAMES
from ui.components import nav, breadcrumb, sec_title, info, warn, hr, section_card

_REASON_LABELS = {
    "time_conflict": "⏰ Time conflict",
    "no_seats":      "💺 Full — no seats",
}


def page_change() -> None:
    sid  = st.session_state.student_id
    name = st.session_state.student_name

    nav(f'<span class="uoh-nav-pill"><b>{name}</b> &nbsp;·&nbsp; {sid}</span>')
    breadcrumb([("🏠 Home", "home"), ("🔄 Change Section", None)])

    sec_title("🔄", "Change Section",
              "Select a course to find an alternative section")

    if st.button("← Back to Schedule"):
        st.session_state.page = "home"
        st.session_state.change_course = None
        st.rerun()

    hr()

    # ── Step 1: Pick course ───────────────────────────────────────────────────
    sec_title("📚", "Step 1 — Select Course",
              "Choose from your currently enrolled courses")

    schedule_df = load_student_schedule(sid)
    if schedule_df.empty:
        warn("No registered courses found.")
        return

    unique = (
        schedule_df[["Code", "Course_name", "Hours", "Days", "STime", "ETim"]]
        .drop_duplicates("Code")
        .sort_values("Code")
    )

    options = ["— Select a course —"] + [
        f"{r['Code']} — {r['Course_name']}"
        for _, r in unique.iterrows()
    ]
    sel = st.selectbox("select_course_change", options, label_visibility="collapsed")

    if sel == "— Select a course —":
        info("Choose one of your enrolled courses to find alternative sections.")
        return

    sel_code = sel.split(" — ")[0].strip()
    cur_rows = schedule_df[schedule_df["Code"] == sel_code]

    if not cur_rows.empty:
        r  = cur_rows.iloc[0]
        dc = str(r.get("Days") or "—")
        info(
            f"<b>Currently enrolled:</b> &nbsp;"
            f"CRN {', '.join(str(c) for c in cur_rows['Cec'].unique())} &nbsp;·&nbsp; "
            f"{r.get('Course_name','—')} &nbsp;·&nbsp; "
            f"{DAY_NAMES.get(dc, dc)} &nbsp;"
            f"{r.get('STime','—')} – {r.get('ETim','—')}"
        )

    hr()

    # ── Step 2: Algorithm → top 3 sections ───────────────────────────────────
    sec_title("⭐", "Step 2 — Best Available Sections",
              "AI-ranked top 3 conflict-free sections (IntervalTree + 5-criteria scoring)")

    with st.spinner("⏳ Running conflict detection and scoring…"):
        alts_df, current_crns, rejected = get_available_alternatives(sid, sel_code)

    if alts_df.empty:
        warn("No conflict-free sections found — all alternatives clash with your schedule "
             "or are fully booked.")
        if rejected:
            hr()
            _render_rejected_panel(rejected, sel_code)
        return

    top3 = alts_df.head(3)
    info(
        f"Found <b>{len(alts_df)}</b> conflict-free section(s) — "
        f"showing the top <b>{len(top3)}</b> ranked by AI score. "
        f"Conflicting sections were hidden automatically."
    )

    cards_container = st.container()
    with cards_container:
        for rank, (_, row) in enumerate(top3.iterrows()):
            row_dict = row.to_dict()
            is_fallback = bool(row_dict.get("fallback", False))
            btn_label   = "⚠️ Join Waitlist" if is_fallback else "✅ Select this section"
            if section_card(
                row_dict, rank,
                btn_label=btn_label,
                key=f"ch_{int(row['Cec'])}_{rank}",
            ):
                st.session_state.update({
                    "confirm_crn":  int(row["Cec"]),
                    "confirm_mode": "change",
                    "confirm_old":  current_crns,
                    "confirm_data": row_dict,
                    "page":         "confirm",
                })
                st.rerun()

    if rejected:
        hr()
        _render_rejected_panel(rejected, sel_code)


def _render_rejected_panel(rejected: list[dict], course_code: str) -> None:
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
