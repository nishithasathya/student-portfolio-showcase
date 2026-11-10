from conftest import register

from app.extensions import db
from app.models import User


def test_password_is_hashed_not_plaintext(app, client):
    register(client, password="supersecret-password")

    with app.app_context():
        user = db.session.query(User).filter_by(email="owner@example.com").first()
        assert user.password_hash != "supersecret-password"
        assert "supersecret-password" not in user.password_hash
        assert user.check_password("supersecret-password")
        assert not user.check_password("wrong-password")


def test_session_cookies_are_hardened(app):
    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"


def test_not_found_response_has_no_stack_trace(client):
    register(client)
    response = client.put("/portfolio/skills/999999", json={"name": "x"})

    assert response.status_code == 404
    assert set(response.json.keys()) == {"error"}
    assert "Traceback" not in response.get_data(as_text=True)


def test_invalid_login_error_does_not_reveal_which_field_was_wrong(client):
    register(client)
    client.post("/auth/logout")

    wrong_password = client.post(
        "/auth/login", json={"email": "owner@example.com", "password": "wrong"}
    )
    unknown_email = client.post(
        "/auth/login", json={"email": "nobody@example.com", "password": "wrong"}
    )

    assert wrong_password.status_code == 401
    assert unknown_email.status_code == 401
    assert wrong_password.json["error"] == unknown_email.json["error"]


def test_logout_invalidates_session_immediately(client):
    register(client)
    client.post("/auth/logout")

    response = client.get("/portfolio")

    assert response.status_code == 401
