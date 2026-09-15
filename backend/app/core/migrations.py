# backend/app/core/migrations.py

import os
import sqlite3
import uuid
from urllib.parse import urlparse

from app.core.config import DATABASE_URL


def _sqlite_path(database_url: str) -> str:
    parsed = urlparse(database_url)

    if parsed.scheme != "sqlite":
        raise ValueError(
            "Only sqlite databases are supported "
            "for automatic migrations."
        )

    path = parsed.path

    if parsed.netloc:
        path = os.path.join(
            parsed.netloc,
            parsed.path,
        )

    return path.lstrip("/")


def ensure_database_schema():
    if not DATABASE_URL.startswith(
        "sqlite"
    ):
        print(
            "[Migration] skipping automatic "
            "schema check — not SQLite"
        )
        return

    db_path = _sqlite_path(
        DATABASE_URL
    )

    if not os.path.exists(db_path):
        print(
            f"[Migration] sqlite file not found: "
            f"{db_path}"
        )
        return

    conn = sqlite3.connect(
        db_path
    )

    try:
        cursor = conn.cursor()

        # ---------------------------------------------------------
        # USERS
        # ---------------------------------------------------------
        cursor.execute(
            "PRAGMA table_info(users)"
        )

        user_columns = {
            row[1]
            for row in cursor.fetchall()
        }

        if not user_columns:
            print(
                "[Migration] users table does not exist"
            )
            return

        user_migrations = [
            (
                "username",
                "TEXT",
            ),
            (
                "alerts_enabled",
                "BOOLEAN DEFAULT 0",
            ),
            (
                "alert_interval",
                "TEXT DEFAULT '6h'",
            ),
            (
                "consent_given",
                "BOOLEAN DEFAULT 0",
            ),
            (
                "consent_date",
                "DATETIME",
            ),
            (
                "verified_email",
                "BOOLEAN DEFAULT 0",
            ),
            (
                "email_verification_token",
                "TEXT",
            ),
            (
                "email_verification_expires_at",
                "DATETIME",
            ),
            (
                "unsubscribe_token",
                "TEXT",
            ),
            (
                "country",
                "TEXT DEFAULT 'Germany'",
            ),
            (
                "city",
                "TEXT",
            ),
            (
                "keywords",
                "TEXT",
            ),
            (
                "language",
                "TEXT DEFAULT 'de'",
            ),
            (
                "employment_type",
                "TEXT DEFAULT 'all'",
            ),
            (
                "job_category",
                "TEXT DEFAULT 'all'",
            ),
            (
                "min_salary",
                "INTEGER",
            ),
            (
                "max_salary",
                "INTEGER",
            ),
        ]

        for (
            column_name,
            column_definition,
        ) in user_migrations:

            if column_name not in user_columns:
                print(
                    "[Migration] adding column: "
                    f"users.{column_name}"
                )

                cursor.execute(
                    "ALTER TABLE users "
                    f"ADD COLUMN {column_name} "
                    f"{column_definition}"
                )

                user_columns.add(
                    column_name
                )

        # ---------------------------------------------------------
        # JOBS
        # ---------------------------------------------------------
        cursor.execute(
            "PRAGMA table_info(jobs)"
        )

        job_columns = {
            row[1]
            for row in cursor.fetchall()
        }

        if "date" not in job_columns:
            print(
                "[Migration] adding column: jobs.date"
            )

            cursor.execute(
                "ALTER TABLE jobs "
                "ADD COLUMN date TEXT"
            )

            job_columns.add(
                "date"
            )

        # ---------------------------------------------------------
        # USER DEFAULTS / BACKFILL
        # ---------------------------------------------------------
        cursor.execute(
            "UPDATE users "
            "SET language = 'de' "
            "WHERE language IS NULL "
            "OR language = ''"
        )

        cursor.execute(
            "UPDATE users "
            "SET employment_type = 'all' "
            "WHERE employment_type IS NULL "
            "OR employment_type = ''"
        )

        cursor.execute(
            "UPDATE users "
            "SET job_category = 'all' "
            "WHERE job_category IS NULL "
            "OR job_category = ''"
        )

        # ---------------------------------------------------------
        # UNSUBSCRIBE TOKENS
        # ---------------------------------------------------------
        if "unsubscribe_token" in user_columns:

            cursor.execute(
                "SELECT id "
                "FROM users "
                "WHERE unsubscribe_token IS NULL "
                "OR unsubscribe_token = ''"
            )

            missing_tokens = cursor.fetchall()

            for (
                user_id,
            ) in missing_tokens:

                cursor.execute(
                    "UPDATE users "
                    "SET unsubscribe_token = ? "
                    "WHERE id = ?",
                    (
                        uuid.uuid4().hex,
                        user_id,
                    ),
                )

        conn.commit()

        print(
            "[Migration] ✅ database schema "
            "is up to date"
        )

    except Exception as exc:
        conn.rollback()

        print(
            f"[Migration] ❌ failed: {exc}"
        )

    finally:
        conn.close()