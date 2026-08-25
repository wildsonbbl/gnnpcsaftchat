"pywebview gui"

# pylint: disable = W0611

# gui.py
import os
import socket
import sys
import threading
import webbrowser
from pathlib import Path

import bootstrap5
import django
import feos
import webview
import whitenoise
from decouple import config
from django.core.management import call_command, execute_from_command_line
from google.adk.sessions.migration import _schema_check_utils, migration_runner
from uvicorn import run

import app.asgi
import app.wsgi
from app import _version
from app import settings as app_settings
from app.cpu_compat import show_compatibility_warning, supports_avx2
from chat import logger

webview.settings["OPEN_EXTERNAL_LINKS_IN_BROWSER"] = False


def _find_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("localhost", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def _redirect_std_streams_to_devnull():
    """Prevent PyInstaller-hidden console apps from crashing on stdout/stderr."""
    sys.stdout = open(os.devnull, "w", encoding="utf-8")  # pylint: disable=R1732
    sys.stderr = open(os.devnull, "w", encoding="utf-8")  # pylint: disable=R1732


def start_django_server(port: int):
    """Start the ASGI app on a specific local port."""
    _redirect_std_streams_to_devnull()

    # Run the server on the dynamic port without the auto-reloader
    # execute_from_command_line(
    #     [sys.argv[0], "runserver", f"127.0.0.1:{port}", "--noreload"]
    # )

    run("app.asgi:application", port=port, log_config=None)


class WindowAPI:
    "window api"

    def __init__(self, port):
        self.port = port

    def open_link(self, url: str):
        "open nav link in new window"
        if self.check_url(url):
            webview.create_window(
                "GNNPCSAFT CHAT - New Window",
                url,
                width=800,
                height=600,
                resizable=True,
            )
        else:
            webbrowser.open(url)

    def check_url(self, url: str):
        "check url"
        return url.startswith(f"http://localhost:{self.port}") or url.startswith("/")


# Ensure local DB migrations are applied before starting the server
def ensure_db_migrated():
    """Ensure the user's local database has been migrated.

    Creates a small flag file under `LOCAL_APP_DATA` to avoid
    running migrations on every startup. Uses Django's
    management `migrate --noinput` and google adks' migration_runner
    when necessary.
    """
    try:
        migrate_flag = (
            Path(app_settings.LOCAL_APP_DATA) / f".db_migrated_v{_version.__version__}"
        )

        if not migrate_flag.exists():
            logger.info("Running Django migrations (ensure_db_migrated)")

            django.setup()

            call_command("migrate", "--noinput")
            check_chat_db()

            migrate_flag.write_text("ok")
            logger.info("Database migrations completed")
        else:
            logger.info("Migrations already applied (flag exists)")
    except RuntimeError:
        logger.exception("Failed to ensure database migrated")


def check_chat_db():
    "Ensure the user's local chat database is compatible with google adk updates"

    assert isinstance(app_settings.DB_CHAT_PATH, Path)
    db_url = "sqlite+aiosqlite:///" + str(app_settings.DB_CHAT_PATH)
    db_url_bkp = db_url + "-bkp"

    if (
        app_settings.DB_CHAT_PATH.exists()
        and _schema_check_utils.LATEST_SCHEMA_VERSION
        != _schema_check_utils.get_db_schema_version(db_url)
    ):
        if os.path.exists(str(app_settings.DB_CHAT_PATH) + "-bkp"):
            os.remove(str(app_settings.DB_CHAT_PATH) + "-bkp")
        os.rename(
            str(app_settings.DB_CHAT_PATH),
            str(app_settings.DB_CHAT_PATH) + "-bkp",
        )

        migration_runner.upgrade(
            source_db_url=db_url_bkp,
            dest_db_url=db_url,
        )


def start_app():
    """Bootstrap migrations, launch the local server, and open the desktop window."""
    if not supports_avx2():
        show_compatibility_warning()
        return

    port = _find_free_port()

    ensure_db_migrated()
    django_thread = threading.Thread(
        target=start_django_server,
        args=(port,),
        daemon=True,
    )
    django_thread.start()

    api = WindowAPI(port)
    webview.create_window(
        "GNNPCSAFT CHAT",
        f"http://localhost:{port}",
        width=800,
        height=600,
        maximized=True,
        js_api=api,
    )
    webview.start()


if __name__ == "__main__":
    start_app()
