"""
engine/scoring.py — 5-criteria scoring function (Step 6).

Algorithm (base = 3, clamped to 1-5):
  1. Morning preference   +1 if start ≤ 10:00 AM  /  -1 if start ≥ 13:00
  2. Seat availability    +1 if ≥ 10 open seats
  3. Day distribution     +1 new study day  /  -1 if same day already has ≥ 2 classes
  4. Back-to-back gap     -1 if gap to adjacent class on same day < 10 min
  5. Instructor variety   +1 if instructor is new (not in current schedule)
"""

import pandas as pd

from engine.time_utils import DAY_NAMES, to_minutes


def score_section(
    row: dict,
    schedule_df: pd.DataFrame,
    exclude_crns: list[int] | None = None,
) -> tuple[int, list[str]]:
    """
    Score a candidate section from 1 to 5 stars.

    Args:
        row:          Raw DB row dict for the candidate section.
        schedule_df:  Student's current schedule DataFrame.
        exclude_crns: CRNs to ignore in the reference schedule
                      (e.g., the course being replaced).

    Returns:
        (score, criteria_log) where criteria_log is a human-readable
        list of strings explaining each adjustment.
    """
    score = 3
    log   = ["Base score: ⭐⭐⭐ (3)"]

    s_m = to_minutes(row.get("start_time") or row.get("STime"))
    e_m = to_minutes(row.get("end_time")   or row.get("ETim"))

    # Reference schedule (may exclude the replaced course)
    ref_df = schedule_df
    if exclude_crns:
        ref_df = schedule_df[~schedule_df["Cec"].isin(exclude_crns)]

    # ── 1. Morning preference ─────────────────────────────────────────────────
    if s_m is not None:
        if s_m <= 10 * 60:
            score += 1
            log.append("✅ +1  Morning time (start ≤ 10:00)")
        elif s_m >= 13 * 60:
            score -= 1
            log.append("⚠️ −1  Afternoon time (start ≥ 13:00)")
        else:
            log.append("➡️  0  Mid-morning time (no adjustment)")

    # ── 2. Seat availability ──────────────────────────────────────────────────
    cap  = int(row.get("max_capacity") or 30)
    enr  = int(row.get("total_students") or 0)
    free = cap - enr
    if free >= 10:
        score += 1
        log.append(f"✅ +1  Good availability ({free} seats open)")
    elif free >= 1:
        log.append(f"➡️  0  Limited seats ({free} open)")
    else:
        log.append("⚠️  0  Section almost full")

    # ── 3. Day distribution ───────────────────────────────────────────────────
    current_days  = set(ref_df["Days"].dropna().unique())
    section_day   = str(row.get("days") or row.get("Days") or "")

    if section_day and section_day not in current_days:
        score += 1
        log.append(f"✅ +1  New study day ({DAY_NAMES.get(section_day, section_day)})")
    elif section_day:
        same_day_count = len(ref_df[ref_df["Days"] == section_day])
        if same_day_count >= 2:
            score -= 1
            log.append(
                f"⚠️ −1  Crowded day — "
                f"{same_day_count} classes already on {DAY_NAMES.get(section_day, section_day)}"
            )
        else:
            log.append("➡️  0  Acceptable day load")

    # ── 4. Back-to-back gap ───────────────────────────────────────────────────
    if s_m and section_day and e_m:
        penalty = False
        for _, ex in ref_df[ref_df["Days"] == section_day].iterrows():
            gap_before = s_m - (ex["end_min"] or 0)
            gap_after  = (ex["start_min"] or 0) - e_m
            if 0 < gap_before < 10 or 0 < gap_after < 10:
                penalty = True
                break
        if penalty:
            score -= 1
            log.append("⚠️ −1  Back-to-back gap < 10 min")
        else:
            log.append("✅  0  Comfortable gap between classes")

    # ── 5. Instructor variety ─────────────────────────────────────────────────
    instr = (row.get("instructor") or "").strip().lower()
    existing_instructors = {
        str(i).strip().lower()
        for i in ref_df["instructor"].dropna().unique()
    }
    if instr and instr not in existing_instructors:
        score += 1
        log.append("✅ +1  New instructor (variety)")
    elif instr:
        log.append("➡️  0  Same instructor as existing course")

    final = max(1, min(5, score))
    log.append(f"─────────────  Final: {'⭐' * final} ({final}/5)")
    return final, log
