"""
engine/time_utils.py — Time conversion helpers + day mapping constants.
"""

from datetime import time, timedelta

# Day code → index used by IntervalTree encoding
DAY_IDX: dict[str, int] = {
    "S": 0,   # Sunday
    "M": 1,   # Monday
    "T": 2,   # Tuesday
    "W": 3,   # Wednesday
    "R": 4,   # Thursday
    "U": 5,   # Saturday
    "F": 6,   # Friday
}

# Day code → full English name
DAY_NAMES: dict[str, str] = {
    "S": "Sunday",
    "M": "Monday",
    "T": "Tuesday",
    "W": "Wednesday",
    "R": "Thursday",
    "U": "Saturday",
    "F": "Friday",
}


def to_minutes(t) -> int | None:
    """Convert a datetime.time, datetime.timedelta, or 'HH:MM' string to total minutes."""
    if t is None:
        return None
    if isinstance(t, timedelta):
        total = int(t.total_seconds())
        return total // 60
    if isinstance(t, time):
        return t.hour * 60 + t.minute
    try:
        h, m = str(t)[:5].split(":")
        return int(h) * 60 + int(m)
    except Exception:
        return None


def fmt_time(t) -> str:
    """Format a time value as 'HH:MM', or '—' if unavailable."""
    if t is None:
        return "—"
    if isinstance(t, timedelta):
        total = int(t.total_seconds())
        h, m = divmod(total // 60, 60)
        return f"{h:02d}:{m:02d}"
    if isinstance(t, time):
        return f"{t.hour:02d}:{t.minute:02d}"
    mins = to_minutes(t)
    if mins is None:
        return "—"
    return f"{mins // 60:02d}:{mins % 60:02d}"
