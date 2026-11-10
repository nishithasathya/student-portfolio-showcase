from flask import jsonify


class AppError(Exception):
    status_code = 500


class ValidationError(AppError):
    status_code = 400


class AuthenticationError(AppError):
    status_code = 401


class ForbiddenError(AppError):
    status_code = 403


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(err):
        return jsonify({"error": str(err)}), err.status_code

    @app.errorhandler(404)
    def handle_404(_err):
        return jsonify({"error": "Resource not found."}), 404

    @app.errorhandler(401)
    def handle_401(_err):
        return jsonify({"error": "Authentication required."}), 401

    @app.errorhandler(405)
    def handle_405(_err):
        return jsonify({"error": "Method not allowed."}), 405

    @app.errorhandler(500)
    def handle_500(err):
        app.logger.exception("Unhandled server error", exc_info=err)
        return jsonify({"error": "Internal server error."}), 500
