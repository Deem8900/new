"""
db/connection.py — Database connection helpers (MySQL via PyMySQL).
Set MYSQL_URL in your .env file:
    MYSQL_URL=mysql+pymysql://root:password@localhost:3306/academiq
"""

import os
import warnings
from pathlib import Path
from sqlalchemy import create_engine

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

warnings.filterwarnings("ignore", category=UserWarning, module="pandas")


def _get_mysql_url() -> str:
    return os.environ.get("MYSQL_URL", "").strip()


def _db_url() -> str:
    """Return the MySQL database URL."""
    mysql = _get_mysql_url()
    if mysql:
        if mysql.startswith("mysql://"):
            return mysql.replace("mysql://", "mysql+pymysql://", 1)
        return mysql

    raise RuntimeError(
        "\n\n❌ Database not configured.\n"
        "Create a .env file in the project root and add:\n\n"
        "    MYSQL_URL=mysql+pymysql://root:your_password@localhost:3306/academiq\n\n"
        "Then restart the application."
    )


def get_engine():
    """Return a SQLAlchemy engine for pd.read_sql usage."""
    return create_engine(_db_url())


def get_db():
    """Return a raw PyMySQL connection for write operations."""
    mysql = _get_mysql_url()
    if not mysql:
        raise RuntimeError(
            "\n\n❌ Database not configured.\n"
            "Create a .env file and add MYSQL_URL=mysql+pymysql://root:your_password@localhost:3306/academiq"
        )
    try:
        import pymysql
        from urllib.parse import urlparse
        p = urlparse(mysql)
        return pymysql.connect(
            host=p.hostname, port=p.port or 3306,
            user=p.username, password=p.password,
            database=p.path.lstrip("/"),
            cursorclass=pymysql.cursors.DictCursor,
        )
    except ImportError:
        raise RuntimeError(
            "PyMySQL is not installed. Run: pip install PyMySQL"
        )


def get_raw_cursor(conn):
    """Return a DictCursor (PyMySQL connections already use DictCursor)."""
    return conn.cursor()


def ensure_notifications_table() -> None:
    """
    Create the `notifications` table if it does not already exist.
    Called once at application startup so the notification system works
    even without re-importing the full SQL dump.
    """
    conn = get_db()
    cur = get_raw_cursor(conn)
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS `notifications` (
              `id` int(11) NOT NULL AUTO_INCREMENT,
              `recipient_type` varchar(10) NOT NULL,
              `recipient_id` int(11) NOT NULL,
              `title` varchar(200) NOT NULL,
              `body` text NOT NULL,
              `notif_type` varchar(30) NOT NULL DEFAULT 'info',
              `is_read` tinyint(1) NOT NULL DEFAULT 0,
              `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
              PRIMARY KEY (`id`),
              KEY `idx_notif_recipient` (`recipient_type`,`recipient_id`,`is_read`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        conn.commit()
    except Exception:
        conn.rollback()
    finally:
        cur.close()
        conn.close()
