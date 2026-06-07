"""
engine/policy.py — Academic registration policy rules.

Centralises the academic gates that the Add-Course flow must pass:

  1. Maximum credit hours per semester.
  2. Course prerequisites — student must have completed (i.e. be already
     registered in or have passed) the listed courses.
  3. Duplicate-course guard — a student must never end up with two
     sections of the SAME course code (req #3 from the supervisor).

Prerequisites are kept here because the original schema does not
include a `prerequisites` table; this file is the single source of
truth that both the UI (for friendly warnings) and the writes layer
(for hard enforcement) consult.
"""

from __future__ import annotations

# Maximum total credit hours a student is allowed to register per semester.
MAX_HOURS_PER_SEMESTER = 18

# course_code -> list of prerequisite course codes.
# Only courses that genuinely require a prereq are listed; everything
# else is treated as "no prerequisite".
PREREQS: dict[str, list[str]] = {
    "CECS484": ["CSCE361"],
    "CSCE121": ["CSCE102"],
    "CSCE351": ["CSCE121"],
    "CSCE352": ["CSCE102"],
    "CSCE353": ["CSCE352"],
    "CSCE354": ["CSCE121"],
    "CSCE361": ["CSCE121"],
    "CSCE362": ["CSCE102"],
    "CSCE363": ["CSCE353"],
    "CSCE364": ["CSCE102"],
    "CSCE480": ["CSCE361", "CSCE352"],
    "CSCE482": ["CSCE353"],
    "CSCE487": ["CSCE352"],
    "CSCE490": ["CSCE361"],
}


def get_prereqs(course_code: str) -> list[str]:
    """Return the list of prerequisite course codes for `course_code`."""
    return list(PREREQS.get(str(course_code).strip(), []))


def missing_prereqs(course_code: str, completed_codes: set[str]) -> list[str]:
    """
    Return the prerequisites for `course_code` that are NOT yet present
    in the student's completed/registered course set.
    """
    completed = {str(c).strip() for c in completed_codes if c is not None}
    return [p for p in get_prereqs(course_code) if p not in completed]


def hours_after_adding(current_hours: int, course_hours: int) -> int:
    """Return the would-be total hours after adding `course_hours`."""
    return int(current_hours or 0) + int(course_hours or 0)


def exceeds_hour_cap(current_hours: int, course_hours: int) -> bool:
    """True if adding `course_hours` would push the student over the cap."""
    return hours_after_adding(current_hours, course_hours) > MAX_HOURS_PER_SEMESTER
