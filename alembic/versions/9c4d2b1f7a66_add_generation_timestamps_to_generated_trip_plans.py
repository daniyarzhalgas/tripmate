"""add generation timestamps to generated trip plans

Revision ID: 9c4d2b1f7a66
Revises: 8f9d3a5e2c11
Create Date: 2026-03-14 13:10:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9c4d2b1f7a66"
down_revision: Union[str, Sequence[str], None] = "8f9d3a5e2c11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("generated_trip_plans")}

    if "generation_requested_at" not in columns:
        op.add_column(
            "generated_trip_plans",
            sa.Column("generation_requested_at", sa.DateTime(), nullable=True),
        )

    if "generated_at" not in columns:
        op.add_column(
            "generated_trip_plans",
            sa.Column("generated_at", sa.DateTime(), nullable=True),
        )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("generated_trip_plans")}

    if "generated_at" in columns:
        op.drop_column("generated_trip_plans", "generated_at")

    if "generation_requested_at" in columns:
        op.drop_column("generated_trip_plans", "generation_requested_at")
