"""Fixtures compartidas para todos los tests con Pytest."""
import pytest
from app import create_app, db as _db


@pytest.fixture(scope="session")
def app():
    """
    Crea una instancia de la app configurada para testing.
    Usa SQLite en memoria para aislar completamente los tests.
    """
    flask_app = create_app("testing")
    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.drop_all()


@pytest.fixture()
def client(app):  # pylint: disable=redefined-outer-name
    """Proporciona el cliente de pruebas de Flask."""
    return app.test_client()


@pytest.fixture(autouse=True)
def limpiar_bd(app):  # pylint: disable=redefined-outer-name
    """
    Limpia todas las tablas antes de cada test para garantizar aislamiento.
    autouse=True significa que se aplica a cada test automáticamente.
    """
    with app.app_context():
        for tabla in reversed(_db.metadata.sorted_tables):
            _db.session.execute(tabla.delete())
        _db.session.commit()
    yield


@pytest.fixture()
def tarea_ejemplo(client):  # pylint: disable=redefined-outer-name
    """Crea una tarea de ejemplo y la retorna como dict."""
    respuesta = client.post(
        "/api/tareas",
        json={"titulo": "Estudiar CI/CD", "descripcion": "Revisar GitHub Actions", "prioridad": "alta"},
    )
    assert respuesta.status_code == 201
    return respuesta.get_json()
