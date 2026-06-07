"""
db/writes.py — Database write operations (INSERT / DELETE for registrations).

Each operation fires notifications to both the student and their assigned
advisor (if any) so both parties see real-time updates.
"""

from db.connection import get_db, get_raw_cursor


def _get_course_info(crn: int) -> tuple[str, str]:
    """Return (code, course_name) for a CRN, or ('', '') on failure."""
    conn = get_db()
    cur = get_raw_cursor(conn)
    try:
        cur.execute(
            """
            SELECT s.code, c.course_name
            FROM sections s
            JOIN courses c ON s.code = c.code
            WHERE s.ref_number = %s
            """,
            (int(crn),),
        )
        row = cur.fetchone()
        if row:
            return str(row["code"]), str(row["course_name"])
        return "", ""
    finally:
        cur.close()
        conn.close()


def do_change_section(student_id: int, old_crns: list[int], new_crn: int) -> bool:
    """
    Remove the student's old CRN(s) for a course and register the new one.
    Wrapped in a transaction — rolls back fully on any error.
    """
    conn = get_db()
    cur  = get_raw_cursor(conn)
    try:
        for crn in old_crns:
            cur.execute(
                "DELETE FROM registration WHERE student_id = %s AND crn = %s",
                (student_id, crn),
            )
        cur.execute(
            "INSERT INTO registration (student_id, crn) "
            "SELECT %s, %s WHERE NOT EXISTS ("
            "  SELECT 1 FROM registration WHERE student_id = %s AND crn = %s"
            ")",
            (student_id, new_crn, student_id, new_crn),
        )
        conn.commit()

        # Fire notifications (best-effort, never break the main operation)
        try:
            from db.notifications import notify_section_changed
            code, name = _get_course_info(new_crn)
            notify_section_changed(student_id, old_crns, new_crn, code, name)
        except Exception:
            pass

        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()


def do_add_section(
    student_id: int,
    new_crn: int,
    enforce_policy: bool = True,
) -> bool | tuple[bool, list[str]]:
    """
    Add a new course section to the student's registration.

    When `enforce_policy=True` (default) the call applies the academic
    gates from `engine.policy`:
        * student must not already be in another section of this course
          (req #3 — one ref_number per course code, never two)
        * student must satisfy the course prerequisites
        * the resulting total credit hours must not exceed the cap

    Returns:
        bool                       — when `enforce_policy=False`
        (bool, list[str] reasons)  — when `enforce_policy=True`
                                     reasons is empty on success.
    """
    reasons: list[str] = []

    if enforce_policy:
        try:
            from db.queries import check_add_eligibility
            code, _name = _get_course_info(int(new_crn))
            if code:
                check = check_add_eligibility(int(student_id), code)
                if not check["ok"]:
                    return False, list(check["reasons"])
        except Exception:
            # Don't silently swallow on the strict path — surface a generic
            # reason but still let the caller see we refused.
            return False, ["Could not verify registration policy — try again."]

    conn = get_db()
    cur  = get_raw_cursor(conn)
    try:
        cur.execute(
            "INSERT INTO registration (student_id, crn) "
            "SELECT %s, %s WHERE NOT EXISTS ("
            "  SELECT 1 FROM registration WHERE student_id = %s AND crn = %s"
            ")",
            (student_id, new_crn, student_id, new_crn),
        )
        conn.commit()

        # Fire notifications
        try:
            from db.notifications import notify_course_added
            code, name = _get_course_info(new_crn)
            notify_course_added(student_id, new_crn, code, name)
        except Exception:
            pass

        return (True, reasons) if enforce_policy else True
    except Exception:
        conn.rollback()
        return (False, ["Database error while adding the section."]) \
            if enforce_policy else False
    finally:
        cur.close()
        conn.close()


def do_drop_course(student_id: int, crn: int) -> bool:
    """Remove a specific CRN from the student's registration."""
    # Get course info before deleting
    code, name = "", ""
    try:
        code, name = _get_course_info(crn)
    except Exception:
        pass

    conn = get_db()
    cur  = get_raw_cursor(conn)
    try:
        cur.execute(
            "DELETE FROM registration WHERE student_id = %s AND crn = %s",
            (student_id, crn),
        )
        conn.commit()

        # Fire notifications
        try:
            from db.notifications import notify_course_dropped
            notify_course_dropped(student_id, crn, code, name)
        except Exception:
            pass

        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()
