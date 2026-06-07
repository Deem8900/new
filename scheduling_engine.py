"""
scheduling_engine.py — Backward-compatible re-export wrapper.

All logic now lives in the sub-packages:
  db/       — database connection, auth, queries, writes
  engine/   — time helpers, IntervalTree, scoring

Import from here to keep any external references working.
"""

from db.auth    import authenticate                          # noqa: F401
from db.queries import (                                     # noqa: F401
    load_student_schedule,
    get_available_alternatives,
    get_addable_courses,
    get_available_sections_to_add,
)
from db.writes  import do_change_section, do_add_section    # noqa: F401

from engine.time_utils    import DAY_IDX, DAY_NAMES, to_minutes, fmt_time  # noqa: F401
from engine.interval_tree import build_interval_tree, has_conflict          # noqa: F401
from engine.scoring       import score_section                              # noqa: F401
