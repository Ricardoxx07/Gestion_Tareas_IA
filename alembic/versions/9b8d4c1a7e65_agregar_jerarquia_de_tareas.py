"""agregar jerarquía de tareas

Revision ID: 9b8d4c1a7e65
Revises: 7a4c0e1d92f3
Create Date: 2026-09-05

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9b8d4c1a7e65"
down_revision: Union[str, Sequence[str], None] = "7a4c0e1d92f3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("tareas", sa.Column("tarea_padre_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_tareas_tarea_padre_id",
        "tareas",
        "tareas",
        ["tarea_padre_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_tareas_tarea_padre_id", "tareas", ["tarea_padre_id"])


def downgrade() -> None:
    op.drop_index("ix_tareas_tarea_padre_id", table_name="tareas")
    op.drop_constraint("fk_tareas_tarea_padre_id", "tareas", type_="foreignkey")
    op.drop_column("tareas", "tarea_padre_id")
