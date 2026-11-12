import pytest
from conftest import register

# Every one of these must require authentication (SPS-SEC-002). Listed as a
# single parametrized table so adding a new protected route later means
# adding one line here, not writing a new test function.
PROTECTED_REQUESTS = [
    ("GET", "/portfolio", None),
    ("GET", "/portfolio/profile", None),
    ("PUT", "/portfolio/profile", {"headline": "x"}),
    ("POST", "/portfolio/publish", {"is_published": True}),
    ("POST", "/portfolio/skills", {"name": "x"}),
    ("PUT", "/portfolio/skills/1", {"name": "x"}),
    ("DELETE", "/portfolio/skills/1", None),
    ("POST", "/portfolio/projects", {"title": "x"}),
    ("PUT", "/portfolio/projects/1", {"title": "x"}),
    ("DELETE", "/portfolio/projects/1", None),
    ("POST", "/portfolio/achievements", {"title": "x"}),
    ("PUT", "/portfolio/achievements/1", {"title": "x"}),
    ("DELETE", "/portfolio/achievements/1", None),
    ("GET", "/auth/me", None),
    ("POST", "/auth/logout", None),
]


@pytest.mark.parametrize("method, path, payload", PROTECTED_REQUESTS)
def test_protected_endpoint_requires_authentication(client, method, path, payload):
    response = client.open(path, method=method, json=payload)

    assert response.status_code == 401


def test_cross_user_cannot_edit_or_delete_project(client):
    register(client)
    project_id = client.post("/portfolio/projects", json={"title": "Original"}).json[
        "id"
    ]
    client.post("/auth/logout")

    register(client, email="intruder-project@example.com", display_name="Intruder Two")

    edit = client.put(f"/portfolio/projects/{project_id}", json={"title": "Hacked"})
    delete = client.delete(f"/portfolio/projects/{project_id}")

    assert edit.status_code == 403
    assert delete.status_code == 403


def test_cross_user_cannot_edit_or_delete_achievement(client):
    register(client)
    achievement_id = client.post(
        "/portfolio/achievements", json={"title": "Original"}
    ).json["id"]
    client.post("/auth/logout")

    register(
        client, email="intruder-achievement@example.com", display_name="Intruder Three"
    )

    edit = client.put(
        f"/portfolio/achievements/{achievement_id}", json={"title": "Hacked"}
    )
    delete = client.delete(f"/portfolio/achievements/{achievement_id}")

    assert edit.status_code == 403
    assert delete.status_code == 403


def test_cross_user_cannot_view_unpublished_profile_via_its_own_slug_guess(client):
    register(client)  # owner keeps their portfolio unpublished
    client.post("/auth/logout")

    register(client, email="visitor@example.com", display_name="Visitor")
    response = client.get("/p/ada-owner")

    assert response.status_code == 404
