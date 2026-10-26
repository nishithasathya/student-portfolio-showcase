from flask import Flask, jsonify


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.update(
        SECRET_KEY="development-only-key",
        TESTING=False,
    )

    if test_config:
        app.config.update(test_config)

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