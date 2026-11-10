import os

from flask import Flask, jsonify

from app.errors import register_error_handlers
from app.extensions import db, login_manager


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Render/Heroku-style hosts hand out "postgres://" URLs; SQLAlchemy 1.4+
    # only recognises "postgresql://". Normalise rather than fail at startup.
    database_url = os.environ.get("DATABASE_URL")
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "development-only-key"),
        SQLALCHEMY_DATABASE_URI=database_url
        or f"sqlite:///{os.path.join(app.instance_path, 'portfolio.db')}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        TESTING=False,
    )

    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.session_protection = "strong"

    from app.auth.routes import bp as auth_bp
    from app.portfolio.routes import bp as portfolio_bp
    from app.public.routes import bp as public_bp
    from app.views.routes import bp as views_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(portfolio_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(views_bp)

    register_error_handlers(app)

    with app.app_context():
        db.create_all()

    @app.get("/")
    def home():
        return jsonify(
            {
                "message": "Student Portfolio Showcase API",
                "status": "running",
            }
        )

    @app.get("/health")
    def health():
        return jsonify({"status": "healthy"}), 200

    return app
