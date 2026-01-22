"Module for django models (dbs)."

import json
import os
import shutil
import sqlite3
import time
import uuid

from django.conf import settings
from django.db import models

from . import logger


class ChatSession(models.Model):
    """Model to store chat sessions"""

    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, default="Unnamed Session")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    messages = models.JSONField(default=list)
    model_name = models.CharField(max_length=100, default="gemini-2.5-flash")
    selected_tools = models.JSONField(default=list)
    selected_mcp_servers = models.JSONField(default=list)

    def __str__(self):
        return f"{self.name} ({self.session_id})"

    def add_message(self, message):
        """Add a message to the session"""
        self.messages.append(message)  # pylint: disable=E1101
        self.save()

    def get_messages(self):
        """Get all messages in the session"""
        return self.messages


def database_compatibility(*args):  # pylint: disable=W0613
    """Check if the local database is compatible."""

    app_db = str(settings.BASE_DIR / "gnnpcsaft.db")
    local_db = str(settings.DB_PATH)

    try:
        logger.info("Verifying database compatibility...")

        if not os.path.exists(local_db):
            logger.info("Local DB not found at %s", local_db)
            if os.path.exists(app_db) and os.path.abspath(app_db) != os.path.abspath(
                local_db
            ):
                os.makedirs(os.path.dirname(local_db) or ".", exist_ok=True)
                shutil.copyfile(app_db, local_db)
                logger.warning("Database created from template %s", app_db)
            else:
                if not os.path.exists(app_db):
                    logger.warning(
                        "Template DB not found at %s; skipping seeding.", app_db
                    )
            return

        if not os.path.exists(app_db):
            logger.error(
                "Template DB not found at %s; skipping "
                "compatibility check to avoid creating a blank DB.",
                app_db,
            )
            return

        def fetch_example(db_path: str):
            try:
                with sqlite3.connect(db_path) as conn:
                    cur = conn.cursor()
                    query = cur.execute(
                        "SELECT name FROM sqlite_master WHERE type='table';"
                    )
                    tables = [name[0] for name in query]
                return tables, None
            except sqlite3.Error as e:
                return None, e

        example_local, err_local = fetch_example(local_db)

        incompatible = (
            err_local is not None
            or example_local is None
            or "gnnmodel_chatsession" in example_local
        )

        if incompatible:
            logger.warning(
                "Old database detected (local=%s, err_local=%s)",
                example_local,
                err_local,
            )

            backup_path = f"{local_db}.old_{int(time.time())}"
            try:
                shutil.copy(local_db, backup_path)
                logger.warning("Old database detected. Backup saved in %s", backup_path)
            except OSError as ex:
                logger.error("Failed to backup DB %s: %s", local_db, ex)
            try:
                update_db(local_db)
                logger.warning("Database updated")
            except sqlite3.Error as ex:
                logger.error(
                    "Failed to update from %s: %s",
                    local_db,
                    ex,
                )

        logger.info("Database is compatible.")
    except Exception as ex:  # pylint: disable=broad-except
        logger.error("Error while checking DB compatibility: %s", ex)


def update_db(local_db):
    "update db"

    with sqlite3.connect(local_db) as conn:
        conn.row_factory = sqlite3.Row  # Allows accessing columns by name
        cursor = conn.cursor()
        try:
            # 1. Fetch all data from source table
            cursor.execute("SELECT * FROM gnnmodel_chatsession")
            rows = cursor.fetchall()

            if not rows:
                logger.info("Source table is empty.")
            else:
                # 2. Prepare columns and placeholders
                columns = rows[0].keys()
                col_names_str = ",".join(columns)
                placeholders = ",".join(["?"] * len(columns))

                clean_rows = []
                for row in rows:
                    row_dict = dict(row)

                    # 3. Sanitize 'selected_mcp_servers' to satisfy JSON_VALID constraint
                    # If value is not None and invalid JSON (e.g. empty string), set to None
                    val = row_dict.get("selected_mcp_servers")
                    if val is not None:
                        try:
                            json.loads(val)
                        except (json.JSONDecodeError, TypeError):
                            row_dict["selected_mcp_servers"] = None

                    # Create tuple in correct column order
                    clean_rows.append(tuple(row_dict[c] for c in columns))

                # 4. Insert cleaned data into destination table
                cursor.executemany(
                    f"INSERT INTO chat_chatsession ({col_names_str}) VALUES ({placeholders})",
                    clean_rows,
                )
                conn.commit()
                logger.info("Transfer complete. Rows transferred: %s", len(clean_rows))

        except sqlite3.Error as e:
            logger.error("An error occurred: %s", e)
