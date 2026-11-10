from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from app.errors import ForbiddenError, NotFoundError
from app.extensions import db
from app.models import Achievement, Project, Skill
from app.validators import (
    require_fields,
    validate_length,
    validate_optional_date,
    validate_optional_url,
)

bp = Blueprint("portfolio", __name__, url_prefix="/portfolio")


def _get_own_portfolio():
    portfolio = current_user.portfolio
    if portfolio is None:
        raise NotFoundError("Portfolio not found for this account.")
    return portfolio


def _get_owned_entry(model, entry_id, portfolio, label):
    """Enforce SPS-SEC-002: only the owning portfolio may act on this record."""
    entry = db.session.get(model, entry_id)
    if entry is None:
        raise NotFoundError(f"{label} not found.")
    if entry.portfolio_id != portfolio.id:
        raise ForbiddenError(f"You do not own this {label.lower()}.")
    return entry


@bp.get("")
@login_required
def get_portfolio():
    return jsonify(_get_own_portfolio().to_owner_dict()), 200


@bp.get("/profile")
@login_required
def get_profile():
    portfolio = _get_own_portfolio()
    return (
        jsonify(
            {
                "display_name": portfolio.display_name,
                "headline": portfolio.headline,
                "bio": portfolio.bio,
            }
        ),
        200,
    )


@bp.put("/profile")
@login_required
def update_profile():
    portfolio = _get_own_portfolio()
    data = request.get_json(silent=True) or {}

    if "display_name" in data:
        portfolio.display_name = validate_length(
            data["display_name"], "display_name", max_length=120, min_length=1
        )
    if "headline" in data:
        portfolio.headline = validate_length(
            data["headline"], "headline", max_length=200
        )
    if "bio" in data:
        portfolio.bio = validate_length(data["bio"], "bio", max_length=4000)

    db.session.commit()
    return jsonify(portfolio.to_owner_dict()), 200


@bp.post("/publish")
@login_required
def set_publish_state():
    portfolio = _get_own_portfolio()
    data = request.get_json(silent=True) or {}
    require_fields(data, ["is_published"])
    portfolio.is_published = bool(data["is_published"])
    db.session.commit()
    return jsonify(
        {"slug": portfolio.slug, "is_published": portfolio.is_published}
    ), 200


# ---------------------------------------------------------------- Skills --


@bp.post("/skills")
@login_required
def add_skill():
    portfolio = _get_own_portfolio()
    data = request.get_json(silent=True) or {}
    require_fields(data, ["name"])

    skill = Skill(
        portfolio_id=portfolio.id,
        name=validate_length(data["name"], "name", max_length=80, min_length=1),
        category=data.get("category"),
        proficiency=data.get("proficiency"),
    )
    db.session.add(skill)
    db.session.commit()
    return jsonify(skill.to_dict()), 201


@bp.put("/skills/<int:skill_id>")
@login_required
def update_skill(skill_id):
    portfolio = _get_own_portfolio()
    skill = _get_owned_entry(Skill, skill_id, portfolio, "Skill")
    data = request.get_json(silent=True) or {}

    if "name" in data:
        skill.name = validate_length(data["name"], "name", max_length=80, min_length=1)
    if "category" in data:
        skill.category = data["category"]
    if "proficiency" in data:
        skill.proficiency = data["proficiency"]

    db.session.commit()
    return jsonify(skill.to_dict()), 200


@bp.delete("/skills/<int:skill_id>")
@login_required
def delete_skill(skill_id):
    portfolio = _get_own_portfolio()
    skill = _get_owned_entry(Skill, skill_id, portfolio, "Skill")
    db.session.delete(skill)
    db.session.commit()
    return "", 204


# -------------------------------------------------------------- Projects --


@bp.post("/projects")
@login_required
def add_project():
    portfolio = _get_own_portfolio()
    data = request.get_json(silent=True) or {}
    require_fields(data, ["title"])

    project = Project(
        portfolio_id=portfolio.id,
        title=validate_length(data["title"], "title", max_length=150, min_length=1),
        description=data.get("description"),
        technologies=data.get("technologies"),
        repo_url=validate_optional_url(data.get("repo_url"), "repo_url"),
        demo_url=validate_optional_url(data.get("demo_url"), "demo_url"),
    )
    db.session.add(project)
    db.session.commit()
    return jsonify(project.to_dict()), 201


@bp.put("/projects/<int:project_id>")
@login_required
def update_project(project_id):
    portfolio = _get_own_portfolio()
    project = _get_owned_entry(Project, project_id, portfolio, "Project")
    data = request.get_json(silent=True) or {}

    if "title" in data:
        project.title = validate_length(
            data["title"], "title", max_length=150, min_length=1
        )
    if "description" in data:
        project.description = data["description"]
    if "technologies" in data:
        project.technologies = data["technologies"]
    if "repo_url" in data:
        project.repo_url = validate_optional_url(data["repo_url"], "repo_url")
    if "demo_url" in data:
        project.demo_url = validate_optional_url(data["demo_url"], "demo_url")

    db.session.commit()
    return jsonify(project.to_dict()), 200


@bp.delete("/projects/<int:project_id>")
@login_required
def delete_project(project_id):
    portfolio = _get_own_portfolio()
    project = _get_owned_entry(Project, project_id, portfolio, "Project")
    db.session.delete(project)
    db.session.commit()
    return "", 204


# ---------------------------------------------------------- Achievements --


@bp.post("/achievements")
@login_required
def add_achievement():
    portfolio = _get_own_portfolio()
    data = request.get_json(silent=True) or {}
    require_fields(data, ["title"])

    achievement = Achievement(
        portfolio_id=portfolio.id,
        title=validate_length(data["title"], "title", max_length=150, min_length=1),
        issuer=data.get("issuer"),
        awarded_on=validate_optional_date(data.get("awarded_on"), "awarded_on"),
        credential_url=validate_optional_url(
            data.get("credential_url"), "credential_url"
        ),
        type=data.get("type", "achievement"),
    )
    db.session.add(achievement)
    db.session.commit()
    return jsonify(achievement.to_dict()), 201


@bp.put("/achievements/<int:achievement_id>")
@login_required
def update_achievement(achievement_id):
    portfolio = _get_own_portfolio()
    achievement = _get_owned_entry(
        Achievement, achievement_id, portfolio, "Achievement"
    )
    data = request.get_json(silent=True) or {}

    if "title" in data:
        achievement.title = validate_length(
            data["title"], "title", max_length=150, min_length=1
        )
    if "issuer" in data:
        achievement.issuer = data["issuer"]
    if "awarded_on" in data:
        achievement.awarded_on = validate_optional_date(
            data["awarded_on"], "awarded_on"
        )
    if "credential_url" in data:
        achievement.credential_url = validate_optional_url(
            data["credential_url"], "credential_url"
        )
    if "type" in data:
        achievement.type = data["type"]

    db.session.commit()
    return jsonify(achievement.to_dict()), 200


@bp.delete("/achievements/<int:achievement_id>")
@login_required
def delete_achievement(achievement_id):
    portfolio = _get_own_portfolio()
    achievement = _get_owned_entry(
        Achievement, achievement_id, portfolio, "Achievement"
    )
    db.session.delete(achievement)
    db.session.commit()
    return "", 204
