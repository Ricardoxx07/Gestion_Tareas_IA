from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base

if TYPE_CHECKING:
    from models.usuario_db import UsuarioDB


class TareaDB(Base):

    __tablename__ = "tareas"

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
