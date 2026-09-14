"""crear usuarios y asociar tareas

Revision ID: 2f31b34f8a10
Revises: 5758d9621eeb
Create Date: 2026-09-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2f31b34f8a10"
down_revision: Union[str, Sequence[str], None] = "5758d9621eeb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Crea usuarios y permite asociar gradualmente las tareas existentes."""
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index(op.f("ix_usuarios_email"), "usuarios", ["email"], unique=True)
    op.create_index(op.f("ix_usuarios_id"), "usuarios", ["id"], unique=False)

    op.add_column(
        "tareas",
        sa.Column("usuario_id", sa.Integer(), nullable=True)
    )
    op.create_index(
        op.f("ix_tareas_usuario_id"),
        "tareas",
        ["usuario_id"],
        unique=False
    )
    op.create_foreign_key(
        "fk_tareas_usuario_id_usuarios",
        "tareas",
        "usuarios",
        ["usuario_id"],
        ["id"]
    )


def downgrade() -> None:
    """Elimina la asociación y después la tabla de usuarios."""
    op.drop_constraint(
        "fk_tareas_usuario_id_usuarios",
        "tareas",
        type_="foreignkey"
    )
    op.drop_index(op.f("ix_tareas_usuario_id"), table_name="tareas")
    op.drop_column("tareas", "usuario_id")

    op.drop_index(op.f("ix_usuarios_id"), table_name="usuarios")
    op.drop_index(op.f("ix_usuarios_email"), table_name="usuarios")
    op.drop_table("usuarios")
