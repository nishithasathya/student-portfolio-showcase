from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required, login_user, logout_user

from app.errors import AuthenticationError, ConflictError
from app.extensions import db, login_manager
from app.models import Portfolio, User
from app.validators import require_fields, validate_email, validate_length

bp = Blueprint("auth", __name__, url_prefix="/auth")


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def _unique_slug(base):
    slug = base
    suffix = 1
    while Portfolio.query.filter_by(slug=slug).first() is not None:
        suffix += 1
        slug = f"{base}-{suffix}"
    return slug


def _slugify(display_name, fallback):
    cleaned = "".join(
        c if c.isalnum() else "-" for c in display_name.strip().lower()
    ).strip("-")
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned or fallback


@bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    require_fields(data, ["email", "password", "display_name"])

    email = validate_email(data["email"])
    password = validate_length(
        data["password"], "password", max_length=128, min_length=8
    )
    display_name = validate_length(
        data["display_name"], "display_name", max_length=120, min_length=1
    )

    if User.query.filter_by(email=email).first() is not None:
        raise ConflictError("An account with this email already exists.")

    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()  # assigns user.id before the portfolio is created

    base_slug = _slugify(display_name, fallback=f"user-{user.id}")
    portfolio = Portfolio(
        user_id=user.id,
        slug=_unique_slug(base_slug),
        display_name=display_name,
    )
    db.session.add(portfolio)
    db.session.commit()

    login_user(user)
    return (
        jsonify({"id": user.id, "email": user.email, "portfolio_slug": portfolio.slug}),
        201,
    )


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    require_fields(data, ["email", "password"])

    user = User.query.filter_by(email=data["email"].strip().lower()).first()
    if user is None or not user.check_password(data["password"]):
        raise AuthenticationError("Invalid email or password.")

    login_user(user)
    return jsonify({"id": user.id, "email": user.email}), 200


@bp.post("/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out."}), 200


@bp.get("/me")
@login_required
def me():
    return jsonify({"id": current_user.id, "email": current_user.email}), 200
