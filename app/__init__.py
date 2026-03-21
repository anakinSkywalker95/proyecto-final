"""Fábrica de la aplicación Flask (Application Factory Pattern)."""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config_name: str = None):
    """
    Crea y configura la instancia de la aplicación Flask.

    Args:
        config_name: Nombre del entorno ('development', 'testing', 'production').
                     Por defecto usa la variable de entorno FLASK_ENV.
    Returns:
        Flask app configurada y lista para usar.
    """
    from app.config import config_map  # pylint: disable=import-outside-toplevel

    app = Flask(__name__)

    env = config_name or os.environ.get("FLASK_ENV", "development")
    cfg_class = config_map.get(env, config_map["development"])
    app.config.from_object(cfg_class())

    db.init_app(app)

    from app.routes import tareas_bp  # pylint: disable=import-outside-toplevel
    from app.errors import register_error_handlers  # pylint: disable=import-outside-toplevel

    app.register_blueprint(tareas_bp)
    register_error_handlers(app)

    with app.app_context():
        db.create_all()

    return app
