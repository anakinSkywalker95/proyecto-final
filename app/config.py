"""Configuración de la aplicación Flask para diferentes entornos."""
import os


class Config:
    """Configuración base."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-insegura")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def get_database_url():
        """Construye la URL de la base de datos desde variables de entorno."""
        return os.environ.get(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5432/tareas_db"
        )

    @property
    def SQLALCHEMY_DATABASE_URI(self):  # pylint: disable=invalid-name
        return self.get_database_url()


class DevelopmentConfig(Config):
    """Configuración para desarrollo."""
    DEBUG = True


class TestingConfig(Config):
    """Configuración para pruebas con SQLite en memoria."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Configuración para producción."""
    DEBUG = False


config_map = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
