"""
Suite de tests para la API de Tareas.

Cubre: creación, listado, obtención, actualización, eliminación
y casos de error de validación.
"""
import pytest


# ── Health Check ──────────────────────────────────────────────────────────────

class TestHealthCheck:
    """Tests para el endpoint de salud."""

    def test_health_retorna_200(self, client):
        """El endpoint /api/health debe responder con HTTP 200."""
        resp = client.get("/api/health")
        assert resp.status_code == 200

    def test_health_contiene_status_ok(self, client):
        """La respuesta de salud debe indicar status ok."""
        resp = client.get("/api/health")
        data = resp.get_json()
        assert data["status"] == "ok"


# ── Crear Tarea (POST) ────────────────────────────────────────────────────────

class TestCrearTarea:
    """Tests para POST /api/tareas."""

    def test_crear_tarea_exitosamente(self, client):
        """Crear una tarea con datos válidos retorna 201 y el objeto creado."""
        resp = client.post(
            "/api/tareas",
            json={"titulo": "Aprender Docker", "prioridad": "alta"},
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["titulo"] == "Aprender Docker"
        assert data["prioridad"] == "alta"
        assert data["completada"] is False
        assert "id" in data

    def test_crear_tarea_sin_titulo_retorna_400(self, client):
        """Crear una tarea sin título debe retornar error 400."""
        resp = client.post("/api/tareas", json={"descripcion": "Sin titulo"})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_crear_tarea_titulo_vacio_retorna_400(self, client):
        """Un título de espacios en blanco debe ser rechazado."""
        resp = client.post("/api/tareas", json={"titulo": "   "})
        assert resp.status_code == 400

    def test_crear_tarea_prioridad_invalida_retorna_400(self, client):
        """Una prioridad no permitida debe retornar error 400."""
        resp = client.post(
            "/api/tareas",
            json={"titulo": "Test", "prioridad": "urgente"},
        )
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_crear_tarea_prioridad_default_es_media(self, client):
        """Sin especificar prioridad, el valor por defecto es 'media'."""
        resp = client.post("/api/tareas", json={"titulo": "Tarea sin prioridad"})
        assert resp.status_code == 201
        assert resp.get_json()["prioridad"] == "media"

    def test_crear_tarea_sin_json_retorna_400(self, client):
        """Enviar petición sin body JSON debe retornar 400."""
        resp = client.post("/api/tareas", data="texto plano", content_type="text/plain")
        assert resp.status_code == 400


# ── Listar Tareas (GET) ───────────────────────────────────────────────────────

class TestListarTareas:
    """Tests para GET /api/tareas."""

    def test_listar_tareas_vacio(self, client):
        """Sin tareas, debe retornar lista vacía con total=0."""
        resp = client.get("/api/tareas")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["tareas"] == []
        assert data["total"] == 0

    def test_listar_tareas_con_datos(self, client, tarea_ejemplo):
        """Con una tarea creada, el listado debe retornar 1 elemento."""
        resp = client.get("/api/tareas")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total"] == 1
        assert data["tareas"][0]["id"] == tarea_ejemplo["id"]

    def test_filtrar_por_completada(self, client):
        """El filtro ?completada=true debe retornar solo tareas completadas."""
        # Crear dos tareas
        client.post("/api/tareas", json={"titulo": "Pendiente"})
        resp_comp = client.post("/api/tareas", json={"titulo": "Completada"})
        tarea_id = resp_comp.get_json()["id"]
        # Marcar una como completada
        client.put(f"/api/tareas/{tarea_id}", json={"completada": True})

        resp = client.get("/api/tareas?completada=true")
        data = resp.get_json()
        assert data["total"] == 1
        assert data["tareas"][0]["completada"] is True

    def test_filtrar_por_prioridad(self, client):
        """El filtro ?prioridad=alta debe retornar solo tareas de alta prioridad."""
        client.post("/api/tareas", json={"titulo": "Tarea baja", "prioridad": "baja"})
        client.post("/api/tareas", json={"titulo": "Tarea alta", "prioridad": "alta"})

        resp = client.get("/api/tareas?prioridad=alta")
        data = resp.get_json()
        assert data["total"] == 1
        assert data["tareas"][0]["prioridad"] == "alta"


# ── Obtener Tarea (GET by ID) ─────────────────────────────────────────────────

class TestObtenerTarea:
    """Tests para GET /api/tareas/<id>."""

    def test_obtener_tarea_existente(self, client, tarea_ejemplo):
        """Debe retornar la tarea correcta por ID."""
        tarea_id = tarea_ejemplo["id"]
        resp = client.get(f"/api/tareas/{tarea_id}")
        assert resp.status_code == 200
        assert resp.get_json()["id"] == tarea_id

    def test_obtener_tarea_inexistente_retorna_404(self, client):
        """Un ID que no existe debe retornar 404."""
        resp = client.get("/api/tareas/9999")
        assert resp.status_code == 404
        assert "error" in resp.get_json()


# ── Actualizar Tarea (PUT) ────────────────────────────────────────────────────

class TestActualizarTarea:
    """Tests para PUT /api/tareas/<id>."""

    def test_actualizar_titulo(self, client, tarea_ejemplo):
        """Debe actualizar el título correctamente."""
        tarea_id = tarea_ejemplo["id"]
        resp = client.put(f"/api/tareas/{tarea_id}", json={"titulo": "Nuevo titulo"})
        assert resp.status_code == 200
        assert resp.get_json()["titulo"] == "Nuevo titulo"

    def test_marcar_como_completada(self, client, tarea_ejemplo):
        """Debe permitir cambiar el estado de completada a True."""
        tarea_id = tarea_ejemplo["id"]
        resp = client.put(f"/api/tareas/{tarea_id}", json={"completada": True})
        assert resp.status_code == 200
        assert resp.get_json()["completada"] is True

    def test_actualizar_prioridad(self, client, tarea_ejemplo):
        """Debe actualizar la prioridad a un valor válido."""
        tarea_id = tarea_ejemplo["id"]
        resp = client.put(f"/api/tareas/{tarea_id}", json={"prioridad": "baja"})
        assert resp.status_code == 200
        assert resp.get_json()["prioridad"] == "baja"

    def test_actualizar_tarea_inexistente_retorna_404(self, client):
        """Actualizar una tarea que no existe debe retornar 404."""
        resp = client.put("/api/tareas/9999", json={"titulo": "No existe"})
        assert resp.status_code == 404

    def test_actualizar_completada_con_no_booleano_retorna_400(self, client, tarea_ejemplo):
        """Pasar un string en completada debe retornar error 400."""
        tarea_id = tarea_ejemplo["id"]
        resp = client.put(f"/api/tareas/{tarea_id}", json={"completada": "si"})
        assert resp.status_code == 400

    def test_actualizar_titulo_vacio_retorna_400(self, client, tarea_ejemplo):
        """Un título vacío en la actualización debe retornar 400."""
        tarea_id = tarea_ejemplo["id"]
        resp = client.put(f"/api/tareas/{tarea_id}", json={"titulo": ""})
        assert resp.status_code == 400


# ── Eliminar Tarea (DELETE) ───────────────────────────────────────────────────

class TestEliminarTarea:
    """Tests para DELETE /api/tareas/<id>."""

    def test_eliminar_tarea_existente(self, client, tarea_ejemplo):
        """Debe eliminar la tarea y retornar mensaje de confirmación."""
        tarea_id = tarea_ejemplo["id"]
        resp = client.delete(f"/api/tareas/{tarea_id}")
        assert resp.status_code == 200
        assert "eliminada" in resp.get_json()["mensaje"]

    def test_eliminar_tarea_ya_no_existe(self, client, tarea_ejemplo):
        """Después de eliminar, GET debe retornar 404."""
        tarea_id = tarea_ejemplo["id"]
        client.delete(f"/api/tareas/{tarea_id}")
        resp = client.get(f"/api/tareas/{tarea_id}")
        assert resp.status_code == 404

    def test_eliminar_tarea_inexistente_retorna_404(self, client):
        """Intentar eliminar una tarea que no existe debe retornar 404."""
        resp = client.delete("/api/tareas/9999")
        assert resp.status_code == 404


# ── Modelo Tarea ──────────────────────────────────────────────────────────────

class TestModeloTarea:
    """Tests unitarios sobre el modelo Tarea."""

    def test_to_dict_contiene_campos_esperados(self, client, tarea_ejemplo):
        """El método to_dict debe incluir todos los campos del modelo."""
        campos = {"id", "titulo", "descripcion", "completada", "prioridad",
                  "creada_en", "actualizada_en"}
        assert campos.issubset(set(tarea_ejemplo.keys()))

    def test_prioridades_validas_definidas(self, client):
        """El modelo debe tener las tres prioridades válidas definidas."""
        from app.models import Tarea  # pylint: disable=import-outside-toplevel
        assert Tarea.PRIORIDADES_VALIDAS == {"baja", "media", "alta"}
