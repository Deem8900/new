"""
engine/interval_tree.py — IntervalTree conflict detection (Step 5).

Encoding:  day_idx * 10_000 + minutes_since_midnight
This maps each (day, time) pair to a unique integer, allowing
O(log n) overlap queries via the IntervalTree library.
"""

import pandas as pd
from intervaltree import IntervalTree

from engine.time_utils import DAY_IDX, to_minutes


def _encode(day: str, minutes: int) -> int:
    """Encode (day, minutes) as a single integer for IntervalTree."""
    return DAY_IDX.get(day, 7) * 10_000 + minutes


def build_interval_tree(
    schedule_df: pd.DataFrame,
    exclude_crns: list[int] | None = None,
) -> IntervalTree:
    """
    Build an IntervalTree from the student's occupied time slots.

    Args:
        schedule_df:  DataFrame from load_student_schedule().
        exclude_crns: CRNs to skip (e.g., the course being changed).

    Returns:
        IntervalTree with one interval per occupied slot.
    """
    tree = IntervalTree()
    for _, row in schedule_df.iterrows():
        if exclude_crns and row["Cec"] in exclude_crns:
            continue

        day = row["Days"]
        s_m = row["start_min"]
        e_m = row["end_min"]

        if day is None or s_m is None or e_m is None or e_m <= s_m:
            continue

        start = _encode(day, s_m)
        end   = _encode(day, e_m)
        if end > start:
            tree.addi(start, end, int(row["Cec"]))

    return tree


def has_conflict(
    tree: IntervalTree,
    day: str,
    s_m: int | None,
    e_m: int | None,
) -> bool:
    """
    Return True if the candidate slot [day, s_m, e_m) overlaps
    any existing interval in the tree.
    """
    if day is None or s_m is None or e_m is None or e_m <= s_m:
        return False
    return bool(tree.overlap(_encode(day, s_m), _encode(day, e_m)))
