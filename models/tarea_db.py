from typing import TYPE_CHECKING

from datetime import date, datetime

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base

if TYPE_CHECKING:
    from models.usuario_db import UsuarioDB


class TareaDB(Base):

    __tablename__ = "tareas"
    __table_args__ = (
        CheckConstraint(
            "prioridad IN ('baja', 'media', 'alta')",
            name="ck_tareas_prioridad_valida"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    nombre: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    completada: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    descripcion: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    fecha_limite: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    prioridad: Mapped[str] = mapped_column(
        String(10),
        default="media",
        server_default="media",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    tarea_padre_id: Mapped[int | None] = mapped_column(
        ForeignKey("tareas.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    tarea_padre: Mapped["TareaDB | None"] = relationship(
        "TareaDB",
        remote_side="TareaDB.id",
        back_populates="subtareas",
    )
    subtareas: Mapped[list["TareaDB"]] = relationship(
        "TareaDB",
        back_populates="tarea_padre",
    )

    # Durante la transición a usuarios puede haber tareas existentes
    # que todavía no tengan un propietario asignado.
    usuario_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id"),
        nullable=True,
        index=True
    )

    usuario: Mapped["UsuarioDB | None"] = relationship(
        "UsuarioDB",
        back_populates="tareas"
    )
