"""add generated trip plans and recommended places

Revision ID: 8f9d3a5e2c11
Revises: 643d25a122fb
Create Date: 2026-03-14 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8f9d3a5e2c11"
down_revision: Union[str, Sequence[str], None] = "643d25a122fb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "generated_trip_plans",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("trip_vacancy_id", sa.Integer(), nullable=False),
        sa.Column("raw_response", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["trip_vacancy_id"], ["trip_vacancies.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("trip_vacancy_id"),
    )

    op.create_table(
        "recommended_places",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("generated_plan_id", sa.Integer(), nullable=False),
        sa.Column("place_id", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("latitude", sa.Numeric(precision=10, scale=7), nullable=True),
        sa.Column("longitude", sa.Numeric(precision=10, scale=7), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=True),
        sa.Column("short_description", sa.Text(), nullable=True),
        sa.Column("why_people_go", sa.Text(), nullable=True),
        sa.Column("why_recommended", sa.Text(), nullable=True),
        sa.Column("highlights", sa.JSON(), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("best_season", sa.JSON(), nullable=True),
        sa.Column("audience", sa.JSON(), nullable=True),
        sa.Column("estimated_cost", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("ticket_price", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("visit_duration_minutes", sa.Integer(), nullable=True),
        sa.Column("best_time_of_day", sa.String(length=50), nullable=True),
        sa.Column("rating", sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column("reviews_count", sa.Integer(), nullable=True),
        sa.Column("image_url", sa.String(length=1000), nullable=True),
        sa.Column("opening_hours", sa.JSON(), nullable=True),
        sa.Column("contact_information", sa.JSON(), nullable=True),
        sa.Column("age_range", sa.JSON(), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["generated_plan_id"], ["generated_trip_plans.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("recommended_places")
    op.drop_table("generated_trip_plans")
