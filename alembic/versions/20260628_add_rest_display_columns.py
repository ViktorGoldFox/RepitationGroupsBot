"""add rest display columns

Revision ID: 20260628_add_rest_display_columns
Revises: 
Create Date: 2026-06-28 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260628_add_rest_display_columns"
down_revision = None
branch_labels = None
depends_on = None


def _format_user_display(username: str | None, full_name: str | None) -> str:
    if username:
        return f"@{username}"

    return full_name or "Unknown user"


def upgrade() -> None:
    migration_context = op.get_context()
    if migration_context.as_sql:
        op.add_column("rests", sa.Column("target_display", sa.String(), nullable=True))
        op.add_column(
            "rests", sa.Column("issued_by_display", sa.String(), nullable=True)
        )
        return

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("rests"):
        return

    existing_columns = {column["name"] for column in inspector.get_columns("rests")}
    if "target_display" not in existing_columns:
        op.add_column(
            "rests", sa.Column("target_display", sa.String(), nullable=True)
        )
    if "issued_by_display" not in existing_columns:
        op.add_column(
            "rests", sa.Column("issued_by_display", sa.String(), nullable=True)
        )

    if not inspector.has_table("users"):
        return

    metadata = sa.MetaData()
    rests = sa.Table("rests", metadata, autoload_with=bind)
    users = sa.Table("users", metadata, autoload_with=bind)

    rest_rows = bind.execute(
        sa.select(
            rests.c.id,
            rests.c.target_t_user_id,
            rests.c.issued_by,
        )
    ).mappings()

    for row in rest_rows:
        target_user = bind.execute(
            sa.select(users.c.t_user_name, users.c.t_user_fullname).where(
                users.c.t_user_id == row["target_t_user_id"]
            )
        ).mappings().first()
        issuer_user = bind.execute(
            sa.select(users.c.t_user_name, users.c.t_user_fullname).where(
                users.c.t_user_id == row["issued_by"]
            )
        ).mappings().first()

        bind.execute(
            rests.update()
            .where(rests.c.id == row["id"])
            .values(
                target_display=_format_user_display(
                    target_user["t_user_name"], target_user["t_user_fullname"]
                )
                if target_user
                else str(row["target_t_user_id"]),
                issued_by_display=_format_user_display(
                    issuer_user["t_user_name"], issuer_user["t_user_fullname"]
                )
                if issuer_user
                else str(row["issued_by"]),
            )
        )


def downgrade() -> None:
    op.drop_column("rests", "issued_by_display")
    op.drop_column("rests", "target_display")
