import pytest

from app import create_app


@pytest.fixture()
def app():
    return create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"})


@pytest.fixture()
def client(app):
    return app.test_client()


def register(
    client, email="owner@example.com", password="supersecret", display_name="Ada Owner"
):
    return client.post(
        "/auth/register",
        json={"email": email, "password": password, "display_name": display_name},
    )
