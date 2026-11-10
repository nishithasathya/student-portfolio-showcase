from conftest import register


def test_register_creates_account_and_portfolio(client):
    response = register(client)

    assert response.status_code == 201
    assert response.json["email"] == "owner@example.com"
    assert response.json["portfolio_slug"] == "ada-owner"


def test_register_rejects_duplicate_email(client):
    register(client)
    response = register(client, display_name="Second Ada")

    assert response.status_code == 409


def test_register_rejects_invalid_email(client):
    response = client.post(
        "/auth/register",
        json={"email": "not-an-email", "password": "supersecret", "display_name": "X"},
    )

    assert response.status_code == 400


def test_register_rejects_short_password(client):
    response = client.post(
        "/auth/register",
        json={"email": "a@b.com", "password": "short", "display_name": "X"},
    )

    assert response.status_code == 400


def test_login_with_valid_credentials(client):
    register(client)
    client.post("/auth/logout")

    response = client.post(
        "/auth/login", json={"email": "owner@example.com", "password": "supersecret"}
    )

    assert response.status_code == 200
    assert response.json["email"] == "owner@example.com"


def test_login_rejects_wrong_password(client):
    register(client)
    client.post("/auth/logout")

    response = client.post(
        "/auth/login", json={"email": "owner@example.com", "password": "wrong-password"}
    )

    assert response.status_code == 401


def test_logout_then_protected_route_requires_auth(client):
    register(client)
    client.post("/auth/logout")

    response = client.get("/portfolio")

    assert response.status_code == 401


def test_profile_create_update_and_view(client):
    register(client)

    update = client.put(
        "/portfolio/profile",
        json={"headline": "AI/ML student", "bio": "I build things."},
    )
    assert update.status_code == 200
    assert update.json["headline"] == "AI/ML student"

    view = client.get("/portfolio/profile")
    assert view.status_code == 200
    assert view.json["bio"] == "I build things."


def test_skill_add_edit_remove(client):
    register(client)

    added = client.post(
        "/portfolio/skills", json={"name": "Python", "proficiency": "advanced"}
    )
    assert added.status_code == 201
    skill_id = added.json["id"]

    edited = client.put(f"/portfolio/skills/{skill_id}", json={"proficiency": "expert"})
    assert edited.status_code == 200
    assert edited.json["proficiency"] == "expert"

    removed = client.delete(f"/portfolio/skills/{skill_id}")
    assert removed.status_code == 204

    missing = client.put(
        f"/portfolio/skills/{skill_id}", json={"proficiency": "expert"}
    )
    assert missing.status_code == 404


def test_project_add_edit_remove(client):
    register(client)

    added = client.post(
        "/portfolio/projects",
        json={"title": "Portfolio App", "repo_url": "https://github.com/x/y"},
    )
    assert added.status_code == 201
    project_id = added.json["id"]

    edited = client.put(
        f"/portfolio/projects/{project_id}", json={"title": "Portfolio App v2"}
    )
    assert edited.status_code == 200
    assert edited.json["title"] == "Portfolio App v2"

    removed = client.delete(f"/portfolio/projects/{project_id}")
    assert removed.status_code == 204


def test_project_rejects_invalid_url(client):
    register(client)

    response = client.post(
        "/portfolio/projects",
        json={"title": "Bad URL Project", "repo_url": "not-a-url"},
    )

    assert response.status_code == 400


def test_achievement_add_edit_remove(client):
    register(client)

    added = client.post(
        "/portfolio/achievements",
        json={
            "title": "Dean's List",
            "awarded_on": "2026-05-01",
            "type": "achievement",
        },
    )
    assert added.status_code == 201
    achievement_id = added.json["id"]

    edited = client.put(
        f"/portfolio/achievements/{achievement_id}", json={"issuer": "University"}
    )
    assert edited.status_code == 200
    assert edited.json["issuer"] == "University"

    removed = client.delete(f"/portfolio/achievements/{achievement_id}")
    assert removed.status_code == 204


def test_publish_and_public_view(client):
    register(client)
    client.post("/portfolio/skills", json={"name": "Python"})

    publish = client.post("/portfolio/publish", json={"is_published": True})
    assert publish.status_code == 200
    assert publish.json["is_published"] is True

    public = client.get("/p/ada-owner")
    assert public.status_code == 200
    assert public.json["display_name"] == "Ada Owner"
    assert len(public.json["skills"]) == 1
    assert "id" not in public.json


def test_unpublished_portfolio_is_not_visible(client):
    register(client)

    response = client.get("/p/ada-owner")

    assert response.status_code == 404


def test_unknown_slug_returns_404(client):
    response = client.get("/p/does-not-exist")

    assert response.status_code == 404


def test_cross_user_cannot_edit_another_owners_skill(client):
    register(client)
    first_skill = client.post("/portfolio/skills", json={"name": "Python"}).json["id"]
    client.post("/auth/logout")

    register(client, email="intruder@example.com", display_name="Intruder")

    response = client.put(f"/portfolio/skills/{first_skill}", json={"name": "Hacked"})

    assert response.status_code == 403
