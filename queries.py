"""
db/queries.py — Read-only database queries.
Covers: student schedule, available sections, addable courses.

Notes on data integrity:
  * Course metadata (`Course_name`, `Hours`) is ALWAYS sourced from the `courses`
    table joined by `code` so that the same course code shows identical name and
    credit hours for every student (Bug Fix 1 — course uniformity).
  * `get_available_alternatives()` and `get_available_sections_to_add()` apply a
    fallback pass that surfaces over-capacity sections (marked `fallback=True`,
    seats `"Full"`) when the strict pipeline returns zero cards, so the supervisor
    requirement of "always render at least one interactable card" is satisfied.
"""

import pandas as pd
from sqlalchemy import text, bindparam

from db.connection import get_engine
from engine.time_utils import to_minutes, fmt_time, DAY_NAMES
from engine.interval_tree import build_interval_tree, has_conflict
from engine.scoring import score_section
from engine.policy import (
    MAX_HOURS_PER_SEMESTER,
    get_prereqs,
    missing_prereqs,
    hours_after_adding,
)


# ── Student academic load ─────────────────────────────────────────────────────

def get_student_load(student_id: int) -> dict:
    """
    Summarise the student's current academic load.

    Returns a dict with:
        total_hours    — sum of credit hours for all registered courses
                         (deduped by course code so a course with multiple
                         time slots is counted once).
        course_codes   — set of registered course codes (used as the
                         "completed for prereq purposes" set in this demo).
        max_hours      — the per-semester cap from the policy module.
        remaining      — how many more hours the student can still take.
    """
    schedule_df = load_student_schedule(int(student_id))
    if schedule_df.empty:
        return {
            "total_hours":  0,
            "course_codes": set(),
            "max_hours":    MAX_HOURS_PER_SEMESTER,
            "remaining":    MAX_HOURS_PER_SEMESTER,
        }

    unique = schedule_df.drop_duplicates(subset=["Code"])
    total  = int(unique["Hours"].fillna(0).astype(int).sum())
    codes  = {str(c) for c in unique["Code"].dropna().unique()}
    return {
        "total_hours":  total,
        "course_codes": codes,
        "max_hours":    MAX_HOURS_PER_SEMESTER,
        "remaining":    max(0, MAX_HOURS_PER_SEMESTER - total),
    }


def check_add_eligibility(student_id: int, course_code: str) -> dict:
    """
    Pre-flight check before showing/adding a course.

    Returns a dict with:
        ok              — bool, True iff the student may add this course
        reasons         — list[str] of human-readable blocking reasons
        warnings        — list[str] of non-blocking warnings
        missing_prereqs — list[str] of prerequisite codes not yet taken
        already_enrolled— bool, True if same course code is already on schedule
        current_hours   — int, current registered hours
        course_hours    — int, credit hours of the course being added
        projected_hours — int, hours after adding
    """
    code = str(course_code).strip()
    load = get_student_load(int(student_id))

    course_hours = _get_course_hours(code)
    projected    = hours_after_adding(load["total_hours"], course_hours)

    reasons:  list[str] = []
    warnings: list[str] = []

    already = code in load["course_codes"]
    if already:
        reasons.append(
            f"Already registered in {code} — a student cannot hold two "
            f"sections of the same course."
        )

    miss = missing_prereqs(code, load["course_codes"])
    if miss:
        reasons.append(
            f"Missing prerequisite(s): {', '.join(miss)}."
        )

    if projected > MAX_HOURS_PER_SEMESTER:
        reasons.append(
            f"Hour limit exceeded — current {load['total_hours']} h "
            f"+ {course_hours} h = {projected} h "
            f"(maximum {MAX_HOURS_PER_SEMESTER} h)."
        )
    elif projected == MAX_HOURS_PER_SEMESTER:
        warnings.append(
            f"This add will reach the semester cap "
            f"({MAX_HOURS_PER_SEMESTER} h)."
        )

    return {
        "ok":               not reasons,
        "reasons":          reasons,
        "warnings":         warnings,
        "missing_prereqs":  miss,
        "already_enrolled": already,
        "current_hours":    load["total_hours"],
        "course_hours":     course_hours,
        "projected_hours":  projected,
        "max_hours":        MAX_HOURS_PER_SEMESTER,
        "prereqs":          get_prereqs(code),
    }


def _get_course_hours(course_code: str) -> int:
    """Return credit hours for a course code (0 if unknown)."""
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT hours FROM courses WHERE code = :c"),
            {"c": str(course_code).strip()},
        ).fetchone()
    return int(row[0]) if row and row[0] is not None else 0


# ── Student schedule ──────────────────────────────────────────────────────────

def load_student_schedule(student_id: int) -> pd.DataFrame:
    """
    Return the student's registered sections as a DataFrame.
    Columns: Cec, Code, Course_name, Hours, Days, STime, ETim,
             Location, instructor, type, start_min, end_min

    Course_name and Hours are pulled from the `courses` table (joined by code)
    so the values are identical for every student that views the same course.
    """
    engine = get_engine()
    query  = text("""
        SELECT
               r.crn          AS "Cec",
               s.code         AS "Code",
               c.course_name  AS "Course_name",
               c.hours        AS "Hours",
               t.days         AS "Days",
               t.start_time   AS "STime",
               t.end_time     AS "ETim",
               t.location     AS "Location",
               s.instructor,
               s.type
        FROM registration r
        JOIN sections  s ON r.crn = s.ref_number
        JOIN courses   c ON s.code = c.code
        LEFT JOIN time_slots t ON t.ref_number = s.ref_number
        WHERE r.student_id = :sid
        ORDER BY s.code, t.days
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"sid": student_id})

    df["start_min"] = df["STime"].apply(to_minutes)
    df["end_min"]   = df["ETim"].apply(to_minutes)
    df["STime"]     = df["STime"].apply(fmt_time)
    df["ETim"]      = df["ETim"].apply(fmt_time)
    return df.sort_values(["Code", "Days"]).reset_index(drop=True)


def get_section_as_schedule_row(crn: int) -> dict | None:
    """
    Return a single dict with the same schema as load_student_schedule rows
    for a given CRN, used to simulate proposed schedule changes.
    Returns None if the CRN is not found.
    """
    engine = get_engine()
    query  = text("""
        SELECT
               s.ref_number   AS `Cec`,
               s.code         AS `Code`,
               c.course_name  AS `Course_name`,
               c.hours        AS `Hours`,
               t.days         AS `Days`,
               t.start_time   AS `STime`,
               t.end_time     AS `ETim`,
               t.location     AS `Location`,
               s.instructor,
               s.type
        FROM sections s
        JOIN courses   c ON s.code = c.code
        LEFT JOIN time_slots t ON t.ref_number = s.ref_number
        WHERE s.ref_number = :crn
        LIMIT 1
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"crn": crn})
    if df.empty:
        return None
    df["start_min"] = df["STime"].apply(to_minutes)
    df["end_min"]   = df["ETim"].apply(to_minutes)
    df["STime"]     = df["STime"].apply(fmt_time)
    df["ETim"]      = df["ETim"].apply(fmt_time)
    return df.iloc[0].to_dict()


def build_proposed_schedule(
    current_df: pd.DataFrame,
    action_type: str,
    new_crn: int,
    old_crns: list[int],
) -> pd.DataFrame:
    """
    Simulate what the schedule would look like if a pending request is approved.
    - action_type='change': remove old_crns rows, add new_crn row.
    - action_type='add':    add new_crn row.
    """
    new_row = get_section_as_schedule_row(new_crn)
    if action_type == "change":
        df = current_df[~current_df["Cec"].isin(old_crns)].copy()
    else:
        df = current_df.copy()
    if new_row is not None:
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    return df.sort_values(["Code", "Days"]).reset_index(drop=True)


# ── Change flow ───────────────────────────────────────────────────────────────

def get_available_alternatives(
    student_id: int,
    course_code: str,
) -> tuple[pd.DataFrame, list[int], list[dict]]:
    """
    Steps 4-6 for the Change flow:
      4. Load all sections for the course.
      5. Build IntervalTree from schedule (excluding current sections) → hide conflicts.
      6. Score each conflict-free section 1-5, return sorted DataFrame + current CRNs.

    Returns (result_df, current_crns, rejected_list) where rejected_list explains
    why each non-chosen section was filtered out (time conflict or full capacity).

    Fallback (Bug Fix 2):
      If the strict pass (capacity enforced) returns zero rows, run a second pass
      that keeps the time-conflict check but relaxes capacity. Each fallback row
      gets `"fallback": True` and `"Seats": "Full"` so the UI can switch the
      button label to "⚠️ Join Waitlist".
    """
    schedule_df  = load_student_schedule(student_id)
    current_crns = schedule_df[schedule_df["Code"] == course_code]["Cec"].tolist()
    tree         = build_interval_tree(schedule_df, exclude_crns=current_crns)

    all_df = _load_sections_for_course(course_code)

    # ── Strict pass ──
    results:  list[dict] = []
    rejected: list[dict] = []

    for _, row in all_df.iterrows():
        if row["Cec"] in current_crns:
            continue

        s_m = to_minutes(row["start_time"])
        e_m = to_minutes(row["end_time"])
        cap = int(row.get("max_capacity") or 30)
        enr = int(row.get("total_students") or 0)
        day = str(row.get("days") or "")

        if has_conflict(tree, row["days"], s_m, e_m):
            rejected.append({
                "Cec":        int(row["Cec"]),
                "Code":       row["Code"],
                "Days":       day,
                "Day_name":   DAY_NAMES.get(day, day),
                "STime":      fmt_time(row.get("start_time")),
                "ETim":       fmt_time(row.get("end_time")),
                "Instructor": row.get("instructor"),
                "Seats":      max(0, cap - enr),
                "reason_code": "time_conflict",
                "reason": (
                    f"Time conflict on {DAY_NAMES.get(day, day) or '—'} "
                    f"({fmt_time(row.get('start_time'))} – "
                    f"{fmt_time(row.get('end_time'))}) with another class."
                ),
            })
            continue

        if enr >= cap:
            rejected.append({
                "Cec":        int(row["Cec"]),
                "Code":       row["Code"],
                "Days":       day,
                "Day_name":   DAY_NAMES.get(day, day),
                "STime":      fmt_time(row.get("start_time")),
                "ETim":       fmt_time(row.get("end_time")),
                "Instructor": row.get("instructor"),
                "Seats":      0,
                "reason_code": "no_seats",
                "reason": f"No seats available — section is full ({enr}/{cap}).",
            })
            continue

        stars, criteria = score_section(
            row.to_dict(), schedule_df, exclude_crns=current_crns
        )
        results.append(_build_result(row, stars, criteria, cap, enr, fallback=False))

    # ── Fallback pass (capacity relaxed, conflicts still enforced) ──
    if not results:
        for _, row in all_df.iterrows():
            if row["Cec"] in current_crns:
                continue

            s_m = to_minutes(row["start_time"])
            e_m = to_minutes(row["end_time"])

            if has_conflict(tree, row["days"], s_m, e_m):
                continue

            cap = int(row.get("max_capacity") or 30)
            enr = int(row.get("total_students") or 0)

            stars, criteria = score_section(
                row.to_dict(), schedule_df, exclude_crns=current_crns
            )
            results.append(_build_result(row, stars, criteria, cap, enr, fallback=True))

        results = sorted(results, key=lambda r: r["Score"], reverse=True)[:3]

    result_df = pd.DataFrame(results)
    if not result_df.empty:
        result_df = result_df.sort_values("Score", ascending=False).reset_index(drop=True)
    return result_df, current_crns, rejected


# ── Add flow ──────────────────────────────────────────────────────────────────

def get_addable_courses(student_id: int) -> list[dict]:
    """
    Return courses the student is NOT yet enrolled in that have sections.
    Course metadata comes exclusively from the `courses` table.
    """
    schedule_df    = load_student_schedule(student_id)
    enrolled_codes = set(schedule_df["Code"].dropna().unique())

    engine = get_engine()
    enrolled_list = list(enrolled_codes) if enrolled_codes else ["__NONE__"]
    query  = text("""
        SELECT DISTINCT c.code, c.course_name, c.hours
        FROM courses c
        JOIN sections s ON s.code = c.code
        JOIN time_slots t ON t.ref_number = s.ref_number
        WHERE c.code NOT IN :enrolled
        ORDER BY c.code
    """).bindparams(bindparam("enrolled", expanding=True))
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"enrolled": enrolled_list})
    return df.to_dict("records")


def get_available_sections_to_add(
    student_id: int,
    course_code: str,
) -> pd.DataFrame:
    """
    Backwards-compatible wrapper: returns only the accepted sections.

    Prefer `get_available_sections_to_add_detailed()` when you also need
    the list of REJECTED sections (with the reason each was filtered
    out) so the UI can explain why a section was not chosen.
    """
    accepted, _rejected = get_available_sections_to_add_detailed(
        student_id, course_code,
    )
    return accepted


def get_available_sections_to_add_detailed(
    student_id: int,
    course_code: str,
) -> tuple[pd.DataFrame, list[dict]]:
    """
    Steps 4-6 for the Add flow: conflict-free, scored sections for a NEW course.

    Returns:
        (accepted_df, rejected_list)
            accepted_df    — DataFrame of conflict-free sections, scored,
                             one row per `ref_number` (deduped — a section
                             with multiple time slots is collapsed).
            rejected_list  — list of dicts describing every section that
                             was filtered out. Each dict has:
                                Cec, Code, Days, STime, ETim, Seats,
                                Instructor, reason, reason_code
                             where `reason_code` is one of:
                                'time_conflict', 'day_conflict',
                                'no_seats', 'duplicate_course'.

    Fallback: if the strict pass returns zero accepted rows, capacity is
    relaxed (each fallback row is marked `fallback=True`, Seats="Full").
    """
    schedule_df = load_student_schedule(student_id)
    tree        = build_interval_tree(schedule_df)
    enrolled    = set(schedule_df["Code"].dropna().astype(str).unique())

    all_df = _load_sections_for_course(course_code)

    accepted: list[dict] = []
    rejected: list[dict] = []

    # Group by ref_number (Cec) so a section with multiple time slots is
    # evaluated as a single section: it is rejected if ANY of its slots
    # conflicts with the student's schedule, accepted only if ALL slots are
    # conflict-free. This guarantees req #3 (one ref_number per course)
    # while still correctly catching multi-meeting clashes.
    if all_df.empty:
        return pd.DataFrame(), rejected

    for cec, slots in all_df.groupby("Cec", sort=False):
        first = slots.iloc[0]
        cap   = int(first.get("max_capacity") or 30)
        enr   = int(first.get("total_students") or 0)

        def _reject(reason_code: str, reason: str, slot_row=first) -> None:
            rejected.append({
                "Cec":         int(cec),
                "Code":        first["Code"],
                "Days":        slot_row.get("days"),
                "Day_name":    DAY_NAMES.get(str(slot_row.get("days")),
                                             str(slot_row.get("days"))),
                "STime":       fmt_time(slot_row.get("start_time")),
                "ETim":        fmt_time(slot_row.get("end_time")),
                "Instructor":  first.get("instructor"),
                "Seats":       max(0, cap - enr),
                "reason_code": reason_code,
                "reason":      reason,
            })

        # Req #3 — never offer a second section of a course already on file.
        if str(first.get("Code")) in enrolled:
            _reject("duplicate_course",
                    "You are already registered in this course — only one "
                    "section per course is allowed.")
            continue

        # Check EVERY meeting slot for this ref_number.
        conflict_slot = None
        for _, slot in slots.iterrows():
            s_m = to_minutes(slot["start_time"])
            e_m = to_minutes(slot["end_time"])
            if has_conflict(tree, slot["days"], s_m, e_m):
                conflict_slot = slot
                break

        if conflict_slot is not None:
            day = str(conflict_slot.get("days") or "")
            _reject("time_conflict",
                    f"Time conflict on {DAY_NAMES.get(day, day) or '—'} "
                    f"({fmt_time(conflict_slot.get('start_time'))} – "
                    f"{fmt_time(conflict_slot.get('end_time'))}) with "
                    f"another class.",
                    slot_row=conflict_slot)
            continue

        if enr >= cap:
            _reject("no_seats",
                    f"No seats available — section is full ({enr}/{cap}).")
            continue

        stars, criteria = score_section(first.to_dict(), schedule_df)
        accepted.append(_build_result(first, stars, criteria, cap, enr,
                                      fallback=False))

    # ── Fallback pass: relax capacity if strict pass yielded nothing ──
    if not accepted:
        for cec, slots in all_df.groupby("Cec", sort=False):
            first = slots.iloc[0]
            if str(first.get("Code")) in enrolled:
                continue
            conflict = False
            for _, slot in slots.iterrows():
                if has_conflict(tree,
                                slot["days"],
                                to_minutes(slot["start_time"]),
                                to_minutes(slot["end_time"])):
                    conflict = True
                    break
            if conflict:
                continue
            cap = int(first.get("max_capacity") or 30)
            enr = int(first.get("total_students") or 0)
            stars, criteria = score_section(first.to_dict(), schedule_df)
            accepted.append(_build_result(first, stars, criteria, cap, enr,
                                          fallback=True))
        accepted = sorted(accepted, key=lambda r: r["Score"], reverse=True)[:3]

    accepted_df = pd.DataFrame(accepted)
    if not accepted_df.empty:
        accepted_df = (accepted_df
                       .sort_values("Score", ascending=False)
                       .reset_index(drop=True))
    return accepted_df, rejected


# ── Internal helpers ──────────────────────────────────────────────────────────

def _load_sections_for_course(course_code: str) -> pd.DataFrame:
    """
    Load every section + time-slot for the given course code. Course metadata
    (`Course_name`, `Hours`) is sourced from the `courses` table — never from
    section-level columns — so all students see identical values.
    """
    engine = get_engine()
    query  = text("""
        SELECT s.ref_number  AS "Cec",
               s.code        AS "Code",
               c.course_name AS "Course_name",
               c.hours       AS "Hours",
               t.days,
               t.start_time,
               t.end_time,
               t.location    AS "Location",
               s.instructor,
               s.type,
               s.total_students,
               t.max_capacity
        FROM sections s
        JOIN courses c ON s.code = c.code
        LEFT JOIN time_slots t ON t.ref_number = s.ref_number
        WHERE s.code = :code
        ORDER BY s.ref_number
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn, params={"code": course_code})


def _build_result(row, stars: int, criteria: list, cap: int, enr: int,
                  fallback: bool = False) -> dict:
    """
    Assemble a section result dict from a raw DB row + scoring output.

    Course_name and Hours come straight from the joined `courses` row so every
    student sees the same canonical values for a given course code.

    When `fallback=True`, the section is over-capacity but conflict-free; the
    Seats field is rendered as the literal string "Full" so the card UI can
    show a waitlist call-to-action.
    """
    return {
        "Cec":         int(row["Cec"]),
        "Code":        row["Code"],
        "Course_name": row["Course_name"],
        "Hours":       int(row["Hours"]),
        "Days":        row["days"],
        "Day_name":    DAY_NAMES.get(str(row["days"]), str(row["days"])),
        "STime":       fmt_time(row["start_time"]),
        "ETim":        fmt_time(row["end_time"]),
        "Location":    row["Location"],
        "Instructor":  row["instructor"],
        "Type":        row["type"],
        "Seats":       "Full" if fallback else cap - enr,
        "Score":       stars,
        "Criteria":    criteria,
        "fallback":    fallback,
    }
