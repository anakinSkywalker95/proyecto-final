"""Manejadores de errores HTTP globales para la aplicación Flask."""
from flask import jsonify


def register_error_handlers(app):
    """Registra manejadores de error 404 y 500 en la app Flask."""

    @app.errorhandler(404)
    def not_found(error):  # pylint: disable=unused-argument
        """Retorna JSON en lugar de HTML para errores 404."""
        return jsonify({"error": "Recurso no encontrado"}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):  # pylint: disable=unused-argument
        """Retorna JSON en lugar de HTML para métodos no permitidos."""
        return jsonify({"error": "Método HTTP no permitido para este endpoint"}), 405

    @app.errorhandler(500)
    def internal_error(error):  # pylint: disable=unused-argument
        """Retorna JSON en lugar de HTML para errores internos."""
        return jsonify({"error": "Error interno del servidor"}), 500
