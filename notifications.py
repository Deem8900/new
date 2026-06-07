"""
db/notifications.py — Notification data layer.

Manages notifications for students and advisors when course actions occur
(add course, drop course, change section, course withdrawal).

Table: `notifications`
  id, recipient_type, recipient_id, title, body, notif_type,
  is_read, created_at
"""

from db.connection import get_db, get_raw_cursor


def create_notification(
    recipient_type: str,
    recipient_id: int,
    title: str,
    body: str,
    notif_type: str = "info",
) -> bool:
    """
    Insert a new notification row.

    recipient_type: 'student' or 'advisor'
    notif_type: 'add_course', 'drop_course', 'change_section', 'withdrawal', 'message', 'info'
    """
    conn = get_db()
    cur = get_raw_cursor(conn)
    try:
        cur.execute(
            """
            INSERT INTO notifications
                (recipient_type, recipient_id, title, body, notif_type, is_read)
            VALUES (%s, %s, %s, %s, %s, 0)
            """,
            (
                str(recipient_type).strip().lower(),
                int(recipient_id),
                str(title),
                str(body),
                str(notif_type),
            ),
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()


def get_notifications(recipient_type: str, recipient_id: int,
                      limit: int = 20) -> list[dict]:
    """Return the most recent notifications for a recipient, newest first."""
    conn = get_db()
    cur = get_raw_cursor(conn)
    try:
        cur.execute(
            """
            SELECT id, recipient_type, recipient_id, title, body,
                   notif_type, is_read, created_at
            FROM notifications
            WHERE recipient_type = %s AND recipient_id = %s
            ORDER BY created_at DESC, id DESC
            LIMIT %s
            """,
            (str(recipient_type).strip().lower(), int(recipient_id), int(limit)),
        )
        return [dict(r) for r in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def get_unread_count(recipient_type: str, recipient_id: int) -> int:
    """Return the number of unread notifications for a recipient."""
    conn = get_db()
    cur = get_raw_cursor(conn)
    try:
        cur.execute(
            """
            SELECT COUNT(*) AS cnt FROM notifications
            WHERE recipient_type = %s AND recipient_id = %s AND is_read = 0
            """,
            (str(recipient_type).strip().lower(), int(recipient_id)),
        )
        row = cur.fetchone()
        return int(row["cnt"]) if row else 0
    finally:
        cur.close()
        conn.close()


def mark_all_read(recipient_type: str, recipient_id: int) -> bool:
    """Mark all notifications as read for a recipient."""
    conn = get_db()
    cur = get_raw_cursor(conn)
    try:
        cur.execute(
            """
            UPDATE notifications SET is_read = 1
            WHERE recipient_type = %s AND recipient_id = %s AND is_read = 0
            """,
            (str(recipient_type).strip().lower(), int(recipient_id)),
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()


def mark_one_read(notification_id: int) -> bool:
    """Mark a single notification as read."""
    conn = get_db()
    cur = get_raw_cursor(conn)
    try:
        cur.execute(
            "UPDATE notifications SET is_read = 1 WHERE id = %s",
            (int(notification_id),),
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()


# ── Convenience helpers: create notifications for common actions ──────────────

def notify_course_added(student_id: int, crn: int, course_code: str,
                        course_name: str = "") -> None:
    """Notify both student and their advisor about a course addition."""
    from db.advisor import get_student_advisor

    label = f"{course_code} — {course_name}" if course_name else course_code

    create_notification(
        "student", student_id,
        "Course Added",
        f"CRN {crn} ({label}) has been added to your schedule.",
        "add_course",
    )

    advisor_id = get_student_advisor(student_id)
    if advisor_id:
        create_notification(
            "advisor", advisor_id,
            "Student Added Course",
            f"Student {student_id} added CRN {crn} ({label}).",
            "add_course",
        )


def notify_course_dropped(student_id: int, crn: int, course_code: str = "",
                          course_name: str = "") -> None:
    """Notify both student and their advisor about a course drop."""
    from db.advisor import get_student_advisor

    label = f"{course_code} — {course_name}" if course_name else f"CRN {crn}"

    create_notification(
        "student", student_id,
        "Course Dropped",
        f"CRN {crn} ({label}) has been removed from your schedule.",
        "drop_course",
    )

    advisor_id = get_student_advisor(student_id)
    if advisor_id:
        create_notification(
            "advisor", advisor_id,
            "Student Dropped Course",
            f"Student {student_id} dropped CRN {crn} ({label}).",
            "drop_course",
        )


def notify_section_changed(student_id: int, old_crns: list[int],
                           new_crn: int, course_code: str = "",
                           course_name: str = "") -> None:
    """Notify both student and their advisor about a section change."""
    from db.advisor import get_student_advisor

    label = f"{course_code} — {course_name}" if course_name else course_code
    old_str = ", ".join(str(c) for c in old_crns)

    create_notification(
        "student", student_id,
        "Section Changed",
        f"Changed from CRN {old_str} to CRN {new_crn} ({label}).",
        "change_section",
    )

    advisor_id = get_student_advisor(student_id)
    if advisor_id:
        create_notification(
            "advisor", advisor_id,
            "Student Changed Section",
            f"Student {student_id} changed from CRN {old_str} to CRN {new_crn} ({label}).",
            "change_section",
        )


def notify_new_message(sender_role: str, advisor_id: int,
                       student_id: int, preview: str = "") -> None:
    """Notify the other party about a new chat message."""
    short = (preview[:60] + "…") if len(preview) > 60 else preview

    if sender_role == "student":
        create_notification(
            "advisor", advisor_id,
            "New Message from Student",
            f"Student {student_id}: {short}",
            "message",
        )
    else:
        create_notification(
            "student", student_id,
            "New Message from Advisor",
            f"Your advisor sent a message: {short}",
            "message",
        )
