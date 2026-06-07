"""
db/auth.py — Student authentication against students_login table.
"""

from db.connection import get_db, get_raw_cursor


def authenticate(username: str, password: str) -> dict | None:
    """
    Return a student info dict if credentials are valid, else None.
    Queries students_login then students tables.
    """
    try:
        uid = int(username.strip())
    except ValueError:
        return None

    conn = get_db()
    cur  = get_raw_cursor(conn)
    try:
        cur.execute(
            "SELECT * FROM students_login WHERE username = %s AND password = %s",
            (uid, password.strip()),
        )
        login = cur.fetchone()
        if not login:
            return None

        cur.execute("SELECT * FROM students WHERE id = %s", (uid,))
        student = cur.fetchone()
        return dict(student) if student else {"id": uid, "name": str(uid)}
    finally:
        cur.close()
        conn.close()
