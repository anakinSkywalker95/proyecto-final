"""Rutas y endpoints CRUD para la entidad Tarea."""
from flask import Blueprint, jsonify, request
from app import db
from app.models import Tarea

tareas_bp = Blueprint("tareas", __name__, url_prefix="/api")


# ── Utilidades ────────────────────────────────────────────────────────────────

def error_response(mensaje: str, codigo: int):
    """Retorna una respuesta de error estandarizada."""
    return jsonify({"error": mensaje}), codigo


def validar_prioridad(prioridad: str):
    """Valida que la prioridad sea un valor permitido."""
    if prioridad not in Tarea.PRIORIDADES_VALIDAS:
        validas = ", ".join(sorted(Tarea.PRIORIDADES_VALIDAS))
        return False, f"Prioridad inválida. Valores permitidos: {validas}"
    return True, None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@tareas_bp.get("/health")
def health_check():
    """
    Verifica el estado de la aplicación
    ---
    tags:
      - Health
    responses:
      200:
        description: App y base de datos funcionando correctamente
    """
    try:
        db.session.execute(db.text("SELECT 1"))
        return jsonify({"status": "ok", "base_de_datos": "conectada"}), 200
    except Exception:  # pylint: disable=broad-except
        return jsonify({"status": "error", "base_de_datos": "desconectada"}), 503


@tareas_bp.get("/tareas")
def listar_tareas():
    """
    Lista todas las tareas
    ---
    tags:
      - Tareas
    parameters:
      - name: completada
        in: query
        type: boolean
        description: Filtrar por estado (true/false)
      - name: prioridad
        in: query
        type: string
        description: Filtrar por prioridad (baja/media/alta)
    responses:
      200:
        description: Lista de tareas obtenida correctamente
    """
    query = Tarea.query

    completada_param = request.args.get("completada")
    if completada_param is not None:
        completada = completada_param.lower() == "true"
        query = query.filter_by(completada=completada)

    prioridad_param = request.args.get("prioridad")
    if prioridad_param:
        query = query.filter_by(prioridad=prioridad_param)

    tareas = query.order_by(Tarea.creada_en.desc()).all()
    return jsonify({"tareas": [t.to_dict() for t in tareas], "total": len(tareas)}), 200


@tareas_bp.get("/tareas/<int:tarea_id>")
def obtener_tarea(tarea_id: int):
    """
    Obtiene una tarea por su ID
    ---
    tags:
      - Tareas
    parameters:
      - name: tarea_id
        in: path
        type: integer
        required: true
        description: ID de la tarea
    responses:
      200:
        description: Tarea encontrada
      404:
        description: Tarea no encontrada
    """
    tarea = db.session.get(Tarea, tarea_id)
    if not tarea:
        return error_response(f"Tarea con id={tarea_id} no encontrada", 404)
    return jsonify(tarea.to_dict()), 200


@tareas_bp.post("/tareas")
def crear_tarea():
    """
    Crea una nueva tarea
    ---
    tags:
      - Tareas
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - titulo
          properties:
            titulo:
              type: string
              example: Mi nueva tarea
            descripcion:
              type: string
              example: Descripción de la tarea
            prioridad:
              type: string
              example: alta
    responses:
      201:
        description: Tarea creada correctamente
      400:
        description: Datos inválidos
    """
    datos = request.get_json(silent=True)
    if not datos:
        return error_response("El cuerpo de la petición debe ser JSON válido", 400)

    titulo = (datos.get("titulo") or "").strip()
    if not titulo:
        return error_response("El campo 'titulo' es obligatorio y no puede estar vacío", 400)

    prioridad = datos.get("prioridad", "media").lower()
    valida, msg = validar_prioridad(prioridad)
    if not valida:
        return error_response(msg, 400)

    tarea = Tarea(
        titulo=titulo,
        descripcion=datos.get("descripcion"),
        prioridad=prioridad,
    )
    db.session.add(tarea)
    db.session.commit()
    return jsonify(tarea.to_dict()), 201


@tareas_bp.put("/tareas/<int:tarea_id>")
def actualizar_tarea(tarea_id: int):
    """
    Actualiza una tarea existente
    ---
    tags:
      - Tareas
    parameters:
      - name: tarea_id
        in: path
        type: integer
        required: true
        description: ID de la tarea
      - name: body
        in: body
        schema:
          type: object
          properties:
            titulo:
              type: string
            descripcion:
              type: string
            completada:
              type: boolean
            prioridad:
              type: string
    responses:
      200:
        description: Tarea actualizada correctamente
      404:
        description: Tarea no encontrada
      400:
        description: Datos inválidos
    """
    tarea = db.session.get(Tarea, tarea_id)
    if not tarea:
        return error_response(f"Tarea con id={tarea_id} no encontrada", 404)

    datos = request.get_json(silent=True)
    if not datos:
        return error_response("El cuerpo de la petición debe ser JSON válido", 400)

    if "titulo" in datos:
        titulo = (datos["titulo"] or "").strip()
        if not titulo:
            return error_response("El campo 'titulo' no puede estar vacío", 400)
        tarea.titulo = titulo

    if "descripcion" in datos:
        tarea.descripcion = datos["descripcion"]

    if "completada" in datos:
        if not isinstance(datos["completada"], bool):
            return error_response("El campo 'completada' debe ser un booleano", 400)
        tarea.completada = datos["completada"]

    if "prioridad" in datos:
        prioridad = datos["prioridad"].lower()
        valida, msg = validar_prioridad(prioridad)
        if not valida:
            return error_response(msg, 400)
        tarea.prioridad = prioridad

    db.session.commit()
    return jsonify(tarea.to_dict()), 200


@tareas_bp.delete("/tareas/<int:tarea_id>")
def eliminar_tarea(tarea_id: int):
    """
    Elimina una tarea por su ID
    ---
    tags:
      - Tareas
    parameters:
      - name: tarea_id
        in: path
        type: integer
        required: true
        description: ID de la tarea a eliminar
    responses:
      200:
        description: Tarea eliminada correctamente
      404:
        description: Tarea no encontrada
    """
    tarea = db.session.get(Tarea, tarea_id)
    if not tarea:
        return error_response(f"Tarea con id={tarea_id} no encontrada", 404)

    db.session.delete(tarea)
    db.session.commit()
    return jsonify({"mensaje": f"Tarea {tarea_id} eliminada correctamente"}), 200