"""add countries and cities tables, convert string fields to FK references

Revision ID: a95bcb91de13
Revises: 02fd820ef1a9
Create Date: 2026-03-30 15:41:17.046952

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a95bcb91de13'
down_revision: Union[str, Sequence[str], None] = '02fd820ef1a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Create new tables
    op.create_table('countries',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_table('cities',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('country_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['country_id'], ['countries.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cities_country_id'), 'cities', ['country_id'], unique=False)

    # 2. Migrate existing data from profiles
    conn = op.get_bind()

    # Collect unique countries from profiles and trip_vacancies
    profile_countries = conn.execute(
        sa.text("SELECT DISTINCT country FROM profiles WHERE country IS NOT NULL AND country != ''")
    ).fetchall()
    tv_countries = conn.execute(
        sa.text("SELECT DISTINCT destination_country FROM trip_vacancies WHERE destination_country IS NOT NULL AND destination_country != ''")
    ).fetchall()

    all_countries = set()
    for row in profile_countries:
        all_countries.add(row[0])
    for row in tv_countries:
        all_countries.add(row[0])

    # Insert countries
    for country_name in all_countries:
        conn.execute(sa.text("INSERT INTO countries (name) VALUES (:name)"), {"name": country_name})

    # Collect unique city-country pairs
    profile_cities = conn.execute(
        sa.text("SELECT DISTINCT city, country FROM profiles WHERE city IS NOT NULL AND city != '' AND country IS NOT NULL AND country != ''")
    ).fetchall()
    tv_cities = conn.execute(
        sa.text("SELECT DISTINCT destination_city, destination_country FROM trip_vacancies WHERE destination_city IS NOT NULL AND destination_city != '' AND destination_country IS NOT NULL AND destination_country != ''")
    ).fetchall()

    all_cities = set()
    for row in profile_cities:
        all_cities.add((row[0], row[1]))
    for row in tv_cities:
        all_cities.add((row[0], row[1]))

    # Insert cities
    for city_name, country_name in all_cities:
        country_row = conn.execute(
            sa.text("SELECT id FROM countries WHERE name = :name"), {"name": country_name}
        ).fetchone()
        if country_row:
            conn.execute(
                sa.text("INSERT INTO cities (name, country_id) VALUES (:name, :country_id)"),
                {"name": city_name, "country_id": country_row[0]}
            )

    # 3. Add FK columns to profiles (using batch for SQLite compatibility)
    with op.batch_alter_table('profiles') as batch_op:
        batch_op.add_column(sa.Column('country_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('city_id', sa.Integer(), nullable=True))

    # Update profiles with FK references
    conn.execute(sa.text("""
        UPDATE profiles SET country_id = (
            SELECT c.id FROM countries c WHERE c.name = profiles.country
        ) WHERE country IS NOT NULL AND country != ''
    """))
    conn.execute(sa.text("""
        UPDATE profiles SET city_id = (
            SELECT ci.id FROM cities ci
            JOIN countries co ON ci.country_id = co.id
            WHERE ci.name = profiles.city AND co.name = profiles.country
        ) WHERE city IS NOT NULL AND city != '' AND country IS NOT NULL AND country != ''
    """))

    # Drop old string columns and add indexes/FKs
    with op.batch_alter_table('profiles') as batch_op:
        batch_op.drop_column('country')
        batch_op.drop_column('city')
        batch_op.create_index(op.f('ix_profiles_country_id'), ['country_id'], unique=False)
        batch_op.create_index(op.f('ix_profiles_city_id'), ['city_id'], unique=False)
        batch_op.create_foreign_key('fk_profiles_country_id', 'countries', ['country_id'], ['id'])
        batch_op.create_foreign_key('fk_profiles_city_id', 'cities', ['city_id'], ['id'])

    # 4. Add FK columns to trip_vacancies
    with op.batch_alter_table('trip_vacancies') as batch_op:
        batch_op.add_column(sa.Column('destination_country_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('destination_city_id', sa.Integer(), nullable=True))

    # Update trip_vacancies with FK references
    conn.execute(sa.text("""
        UPDATE trip_vacancies SET destination_country_id = (
            SELECT c.id FROM countries c WHERE c.name = trip_vacancies.destination_country
        ) WHERE destination_country IS NOT NULL AND destination_country != ''
    """))
    conn.execute(sa.text("""
        UPDATE trip_vacancies SET destination_city_id = (
            SELECT ci.id FROM cities ci
            JOIN countries co ON ci.country_id = co.id
            WHERE ci.name = trip_vacancies.destination_city AND co.name = trip_vacancies.destination_country
        ) WHERE destination_city IS NOT NULL AND destination_city != '' AND destination_country IS NOT NULL AND destination_country != ''
    """))

    # Drop old string columns, add indexes/FKs, set NOT NULL
    with op.batch_alter_table('trip_vacancies') as batch_op:
        batch_op.drop_column('destination_country')
        batch_op.drop_column('destination_city')
        batch_op.create_index(op.f('ix_trip_vacancies_destination_country_id'), ['destination_country_id'], unique=False)
        batch_op.create_index(op.f('ix_trip_vacancies_destination_city_id'), ['destination_city_id'], unique=False)
        batch_op.create_foreign_key('fk_tv_destination_country_id', 'countries', ['destination_country_id'], ['id'])
        batch_op.create_foreign_key('fk_tv_destination_city_id', 'cities', ['destination_city_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('trip_vacancies') as batch_op:
        batch_op.add_column(sa.Column('destination_city', sa.VARCHAR(length=100), nullable=True))
        batch_op.add_column(sa.Column('destination_country', sa.VARCHAR(length=100), nullable=True))

    conn = op.get_bind()
    conn.execute(sa.text("""
        UPDATE trip_vacancies SET destination_country = (
            SELECT c.name FROM countries c WHERE c.id = trip_vacancies.destination_country_id
        )
    """))
    conn.execute(sa.text("""
        UPDATE trip_vacancies SET destination_city = (
            SELECT ci.name FROM cities ci WHERE ci.id = trip_vacancies.destination_city_id
        )
    """))

    with op.batch_alter_table('trip_vacancies') as batch_op:
        batch_op.drop_constraint('fk_tv_destination_city_id', type_='foreignkey')
        batch_op.drop_constraint('fk_tv_destination_country_id', type_='foreignkey')
        batch_op.drop_index(op.f('ix_trip_vacancies_destination_country_id'))
        batch_op.drop_index(op.f('ix_trip_vacancies_destination_city_id'))
        batch_op.drop_column('destination_city_id')
        batch_op.drop_column('destination_country_id')

    with op.batch_alter_table('profiles') as batch_op:
        batch_op.add_column(sa.Column('city', sa.VARCHAR(length=100), nullable=True))
        batch_op.add_column(sa.Column('country', sa.VARCHAR(length=100), nullable=True))

    conn.execute(sa.text("""
        UPDATE profiles SET country = (
            SELECT c.name FROM countries c WHERE c.id = profiles.country_id
        )
    """))
    conn.execute(sa.text("""
        UPDATE profiles SET city = (
            SELECT ci.name FROM cities ci WHERE ci.id = profiles.city_id
        )
    """))

    with op.batch_alter_table('profiles') as batch_op:
        batch_op.drop_constraint('fk_profiles_city_id', type_='foreignkey')
        batch_op.drop_constraint('fk_profiles_country_id', type_='foreignkey')
        batch_op.drop_index(op.f('ix_profiles_country_id'))
        batch_op.drop_index(op.f('ix_profiles_city_id'))
        batch_op.drop_column('city_id')
        batch_op.drop_column('country_id')

    op.drop_index(op.f('ix_cities_country_id'), table_name='cities')
    op.drop_table('cities')
    op.drop_table('countries')
