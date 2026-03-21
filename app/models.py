"""Modelos de base de datos con SQLAlchemy."""
from datetime import datetime, timezone
from app import db


class Tarea(db.Model):
    """Modelo que representa una tarea en el sistema."""

    __tablename__ = "tareas"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    completada = db.Column(db.Boolean, default=False, nullable=False)
    prioridad = db.Column(
        db.String(10),
        nullable=False,
        default="media",
    )
    creada_en = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    actualizada_en = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    PRIORIDADES_VALIDAS = {"baja", "media", "alta"}

    def to_dict(self):
        """Serializa la tarea a un diccionario JSON-compatible."""
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "completada": self.completada,
            "prioridad": self.prioridad,
            "creada_en": self.creada_en.isoformat() if self.creada_en else None,
            "actualizada_en": self.actualizada_en.isoformat() if self.actualizada_en else None,
        }

    def __repr__(self):
        return f"<Tarea {self.id}: {self.titulo}>"
