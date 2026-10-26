from app import create_app


def test_home_endpoint():
    app = create_app({"TESTING": True})
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert response.json["message"] == "Student Portfolio Showcase API"
    assert response.json["status"] == "running"


def test_health_endpoint():
    app = create_app({"TESTING": True})
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json == {"status": "healthy"}