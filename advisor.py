"""
db/advisor.py — Academic-advisor data layer.

All functions use the shared `get_db()` / `get_raw_cursor()` helpers from
`db.connection` so the same MySQL connection settings (and PyMySQL DictCursor
behaviour) used by the rest of the app apply here too.

Tables touched (created in `db/academiq (3).sql`):
  * advisors              — advisor identity
  * advisors_login        — advisor credentials
  * advisor_assignments   — many-to-many advisor↔student
  * advisor_messages      — chat history + course-action requests
"""

from db.connection import get_db, get_raw_cursor


# ── DB migration ──────────────────────────────────────────────────────────────

def ensure_action_old_crns_column() -> None:
    """Add action_old_crns column to advisor_messages if it doesn't exist."""
    conn = get_db()
    cur  = get_raw_cursor(conn)
    try:
        cur.execute("""
            SELECT COUNT(*) AS cnt
            FROM information_schema.columns
            WHERE table_schema = DATABASE()
              AND table_name   = 'advisor_messages'
              AND column_name  = 'action_old_crns'
        """)
        row = cur.fetchone()
        if row and int(row["cnt"]) == 0:
            cur.execute("""
                ALTER TABLE advisor_messages
                ADD COLUMN action_old_crns VARCHAR(200) DEFAULT NULL
            """)
            conn.commit()
    finally:
        cur.close()
        conn.close()


# ── Authentication ────────────────────────────────────────────────────────────

def authenticate_advisor(advisor_id: str, password: str) -> dict | None:
    """
    Verify advisor credentials and return the advisor record on success.

    Returns a dict like {"id": int, "name": str, "department": str} or None.
    """
    try:
        aid = int(str(advisor_id).strip())
    except (TypeError, ValueError):
        return None

    conn = get_db()
    cur  = get_raw_cursor(conn)
    try:
        cur.execute(
            "SELECT * FROM advisors_login WHERE advisor_id = %s AND password = %s",
            (aid, str(password).strip()),
        )
        login = cur.fetchone()
        if not login:
            return None

        cur.execute("SELECT * FROM advisors WHERE id = %s", (aid,))
        advisor = cur.fetchone()
        if not advisor:
            return {"id": aid, "name": str(aid), "department": ""}
        return dict(advisor)
    finally:
        cur.close()
        conn.close()


# ── Assignment lookups ────────────────────────────────────────────────────────

def get_advisor_students(advisor_id: int) -> list[dict]:
    """
    List the students assigned to a given advisor.

    Each dict contains: student_id, name, specialization, level.
    Note: the existing `students` table column is `specialistion` (typo), so
    we alias it to `specialization` for the UI.
    """
    conn = get_db()
    cur  = get_raw_cursor(conn)
    try:
        cur.execute(
            """
            SELECT s.id            AS student_id,
                   s.name          AS name,
                   s.specialistion AS specialization,
                   s.level         AS level
            FROM advisor_assignments a
            JOIN students s ON s.id = a.student_id
            WHERE a.advisor_id = %s
            ORDER BY s.name
            """,
            (int(advisor_id),),
        )
        return [dict(r) for r in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def get_student_advisor(student_id: int) -> int | None:
    """Return the advisor_id assigned to this student, or None if not assigned."""
    conn = get_db()
    cur  = get_raw_cursor(conn)
    try:
        cur.execute(
            "SELECT advisor_id FROM advisor_assignments WHERE student_id = %s LIMIT 1",
            (int(student_id),),
        )
        row = cur.fetchone()
        if not row:
            return None
        return int(row["advisor_id"])
    finally:
        cur.close()
        conn.close()


# ── Messaging ─────────────────────────────────────────────────────────────────

def get_messages(advisor_id: int, student_id: int) -> list[dict]:
    """
    Return all messages between the given advisor and student in chronological
    order (oldest first).

    Each dict contains: id, sender_role, sender_name, body, timestamp,
    action_type, action_crn, action_old_crns, handled.
    """
    conn = get_db()
    cur  = get_raw_cursor(conn)
    try:
        cur.execute(
            """
            SELECT id,
                   sender_role,
                   sender_name,
                   body,
                   created_at AS timestamp,
                   action_type,
                   action_crn,
                   action_old_crns,
                   handled
            FROM advisor_messages
            WHERE advisor_id = %s AND student_id = %s
            ORDER BY created_at ASC, id ASC
            """,
            (int(advisor_id), int(student_id)),
        )
        return [dict(r) for r in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def send_message(sender_role: str, advisor_id: int, student_id: int,
                 body: str, action_type: str | None = None,
                 action_crn: int | None = None,
                 action_old_crns: list[int] | None = None) -> bool:
    """
    Insert a new chat row.

    Sender name is resolved automatically from the `advisors` / `students`
    tables based on `sender_role` so the UI can render it without an extra
    lookup.

    action_old_crns — list of CRNs to drop (used for 'change' requests).
    """
    role = str(sender_role).strip().lower()
    if role not in ("advisor", "student"):
        return False

    conn = get_db()
    cur  = get_raw_cursor(conn)
    try:
        if role == "advisor":
            cur.execute("SELECT name FROM advisors WHERE id = %s", (int(advisor_id),))
        else:
            cur.execute("SELECT name FROM students WHERE id = %s", (int(student_id),))
        row = cur.fetchone()
        sender_name = (row["name"] if row else None) or ""

        old_crns_str = (
            ",".join(str(c) for c in action_old_crns)
            if action_old_crns else None
        )

        cur.execute(
            """
            INSERT INTO advisor_messages
                (advisor_id, student_id, sender_role, sender_name,
                 body, action_type, action_crn, action_old_crns, handled)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 0)
            """,
            (
                int(advisor_id),
                int(student_id),
                role,
                sender_name,
                str(body),
                action_type,
                int(action_crn) if action_crn is not None else None,
                old_crns_str,
            ),
        )
        conn.commit()

        # Fire notification to the other party (best-effort)
        try:
            from db.notifications import notify_new_message
            notify_new_message(role, int(advisor_id), int(student_id), str(body))
        except Exception:
            pass

        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()


def mark_request_handled(message_id: int) -> bool:
    """Set handled = 1 on the given message row."""
    conn = get_db()
    cur  = get_raw_cursor(conn)
    try:
        cur.execute(
            "UPDATE advisor_messages SET handled = 1 WHERE id = %s",
            (int(message_id),),
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()


def reject_request(message_id: int) -> bool:
    """Mark a request as handled (rejected) without executing any DB change."""
    return mark_request_handled(message_id)


def get_pending_requests(advisor_id: int, student_id: int) -> list[dict]:
    """
    Return only unhandled student requests (action_type is not NULL) for a
    given advisor-student pair, ordered oldest first.
    """
    conn = get_db()
    cur  = get_raw_cursor(conn)
    try:
        cur.execute(
            """
            SELECT id,
                   sender_role,
                   sender_name,
                   body,
                   created_at AS timestamp,
                   action_type,
                   action_crn,
                   action_old_crns,
                   handled
            FROM advisor_messages
            WHERE advisor_id  = %s
              AND student_id  = %s
              AND sender_role = 'student'
              AND action_type IS NOT NULL
              AND handled     = 0
            ORDER BY created_at ASC, id ASC
            """,
            (int(advisor_id), int(student_id)),
        )
        return [dict(r) for r in cur.fetchall()]
    finally:
        cur.close()
        conn.close()
