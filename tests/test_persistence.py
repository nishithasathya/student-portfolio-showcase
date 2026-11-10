import os
import tempfile

from app import create_app
from app.extensions import db


def test_data_persists_across_application_restart():
    """SPS-FR-019 / TC-DB-01: records survive a real process restart, not
    just repeated calls against the same app instance. Two separate
    create_app() calls share one file-backed SQLite database to simulate
    the app being stopped and started again."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    apps = []

    try:
        db_uri = f"sqlite:///{db_path}"

        first_run = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": db_uri})
        apps.append(first_run)
        first_client = first_run.test_client()
        first_client.post(
            "/auth/register",
            json={
                "email": "persist@example.com",
                "password": "supersecret",
                "display_name": "Persist Owner",
            },
        )
        first_client.post("/portfolio/skills", json={"name": "Durability"})

        second_run = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": db_uri})
        apps.append(second_run)
        second_client = second_run.test_client()
        second_client.post(
            "/auth/login",
            json={"email": "persist@example.com", "password": "supersecret"},
        )
        response = second_client.get("/portfolio")

        assert response.status_code == 200
        assert any(skill["name"] == "Durability" for skill in response.json["skills"])
    finally:
        # Close every pooled connection first: Windows cannot delete a file
        # that is still open (WinError 32), unlike Linux/macOS.
        for app in apps:
            with app.app_context():
                db.engine.dispose()
        os.remove(db_path)
