"""agregar datos de planificacion a tareas

Revision ID: 7a4c0e1d92f3
Revises: 2f31b34f8a10
Create Date: 2026-09-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7a4c0e1d92f3"
down_revision: Union[str, Sequence[str], None] = "2f31b34f8a10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("tareas", sa.Column("fecha_limite", sa.Date(), nullable=True))
    op.add_column(
        "tareas",
        sa.Column(
            "prioridad",
            sa.String(length=10),
            server_default="media",
            nullable=False
        )
    )
    op.add_column(
        "tareas",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False
        )
    )
    op.create_check_constraint(
        "ck_tareas_prioridad_valida",
        "tareas",
        "prioridad IN ('baja', 'media', 'alta')"
    )


def downgrade() -> None:
    op.drop_constraint("ck_tareas_prioridad_valida", "tareas", type_="check")
    op.drop_column("tareas", "created_at")
    op.drop_column("tareas", "prioridad")
    op.drop_column("tareas", "fecha_limite")
