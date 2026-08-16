# backend/app/core/migrations.py

import os
import sqlite3
import uuid
from urllib.parse import urlparse

from app.core.config import DATABASE_URL


def _sqlite_path(database_url: str) -> str:
    parsed = urlparse(database_url)
    if parsed.scheme != "sqlite":
        raise ValueError("Only sqlite databases are supported for automatic migrations.")
    path = parsed.path
    if parsed.netloc:
        path = os.path.join(parsed.netloc, parsed.path)
    return path.lstrip("/")


def ensure_user_schema():
    if not DATABASE_URL.startswith("sqlite"):
        print("[Migration] skipping user schema check — not SQLite")
        return

    db_path = _sqlite_path(DATABASE_URL)
    if not os.path.exists(db_path):
        print(f"[Migration] sqlite file not found: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(users)")
        columns = {row[1] for row in cursor.fetchall()}

        if not columns:
            print("[Migration] users table does not exist, skipping")
            return

        # All columns the users table should have.
        # Add new fields here — they will be applied automatically on next startup.
        migrations = [
            ("username",                  "TEXT"),
            ("alerts_enabled",            "BOOLEAN DEFAULT 0"),
            ("alert_interval",            "TEXT DEFAULT '6h'"),
            ("consent_given",             "BOOLEAN DEFAULT 0"),
            ("consent_date",              "DATETIME"),
            ("verified_email",            "BOOLEAN DEFAULT 0"),
            ("email_verification_token",  "TEXT"),
            ("unsubscribe_token",         "TEXT"),
            ("country",                   "TEXT DEFAULT 'Germany'"),
            ("city",                      "TEXT"),
            ("keywords",                  "TEXT"),
            # ── Filter fields that were missing ──────────────────────────────
            ("language",                  "TEXT DEFAULT 'de'"),
            ("employment_type",           "TEXT DEFAULT 'all'"),
            ("job_category",              "TEXT DEFAULT 'all'"),
            ("min_salary",                "INTEGER"),
            ("max_salary",                "INTEGER"),
        ]

        for column_name, column_definition in migrations:
            if column_name not in columns:
                print(f"[Migration] adding column: {column_name}")
                cursor.execute(
                    f"ALTER TABLE users ADD COLUMN {column_name} {column_definition}"
                )
                columns.add(column_name)

        # Backfill default values and missing tokens for legacy rows.
        cursor.execute("UPDATE users SET language = 'de' WHERE language IS NULL OR language = ''")
        cursor.execute("UPDATE users SET employment_type = 'all' WHERE employment_type IS NULL OR employment_type = ''")
        cursor.execute("UPDATE users SET job_category = 'all' WHERE job_category IS NULL OR job_category = ''")

        if "unsubscribe_token" in columns:
            cursor.execute(
                "SELECT id FROM users WHERE unsubscribe_token IS NULL OR unsubscribe_token = ''"
            )
            for (user_id,) in cursor.fetchall():
                cursor.execute(
                    "UPDATE users SET unsubscribe_token = ? WHERE id = ?",
                    (uuid.uuid4().hex, user_id),
                )

        conn.commit()
        print("[Migration] ✅ user schema is up to date")
    except Exception as exc:
        print(f"[Migration] ❌ failed: {exc}")
    finally:
        conn.close()