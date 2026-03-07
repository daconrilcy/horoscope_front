"""backfill prediction planet profile orbs

Revision ID: 20260307_0036
Revises: 20260307_0035
Create Date: 2026-03-07
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260307_0036"
down_revision: Union[str, Sequence[str], None] = "20260307_0035"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ORB_VALUES: dict[str, tuple[float, float]] = {
    "sun": (5.0, 1.5),
    "moon": (4.5, 1.2),
    "mercury": (3.0, 1.0),
    "venus": (3.0, 1.0),
    "mars": (3.0, 1.0),
    "jupiter": (2.5, 0.8),
    "saturn": (2.5, 0.8),
    "uranus": (2.0, 0.6),
    "neptune": (2.0, 0.6),
    "pluto": (2.0, 0.6),
}


def upgrade() -> None:
    connection = op.get_bind()

    reference_versions = sa.table(
        "reference_versions",
        sa.column("id", sa.Integer()),
        sa.column("version", sa.String()),
    )
    planets = sa.table(
        "planets",
        sa.column("id", sa.Integer()),
        sa.column("reference_version_id", sa.Integer()),
        sa.column("code", sa.String()),
    )
    planet_profiles = sa.table(
        "planet_profiles",
        sa.column("planet_id", sa.Integer()),
        sa.column("orb_active_deg", sa.Float()),
        sa.column("orb_peak_deg", sa.Float()),
    )

    reference_id = connection.execute(
        sa.select(reference_versions.c.id).where(reference_versions.c.version == "2.0.0")
    ).scalar_one_or_none()
    if reference_id is None:
        return

    for planet_code, (orb_active, orb_peak) in ORB_VALUES.items():
        planet_id = connection.execute(
            sa.select(planets.c.id).where(
                planets.c.reference_version_id == reference_id,
                planets.c.code == planet_code,
            )
        ).scalar_one_or_none()
        if planet_id is None:
            continue

        connection.execute(
            sa.update(planet_profiles)
            .where(
                planet_profiles.c.planet_id == planet_id,
                sa.or_(
                    planet_profiles.c.orb_active_deg.is_(None),
                    planet_profiles.c.orb_peak_deg.is_(None),
                ),
            )
            .values(
                orb_active_deg=sa.case(
                    (planet_profiles.c.orb_active_deg.is_(None), orb_active),
                    else_=planet_profiles.c.orb_active_deg,
                ),
                orb_peak_deg=sa.case(
                    (planet_profiles.c.orb_peak_deg.is_(None), orb_peak),
                    else_=planet_profiles.c.orb_peak_deg,
                ),
            )
        )


def downgrade() -> None:
    connection = op.get_bind()

    reference_versions = sa.table(
        "reference_versions",
        sa.column("id", sa.Integer()),
        sa.column("version", sa.String()),
    )
    planets = sa.table(
        "planets",
        sa.column("id", sa.Integer()),
        sa.column("reference_version_id", sa.Integer()),
        sa.column("code", sa.String()),
    )
    planet_profiles = sa.table(
        "planet_profiles",
        sa.column("planet_id", sa.Integer()),
        sa.column("orb_active_deg", sa.Float()),
        sa.column("orb_peak_deg", sa.Float()),
    )

    reference_id = connection.execute(
        sa.select(reference_versions.c.id).where(reference_versions.c.version == "2.0.0")
    ).scalar_one_or_none()
    if reference_id is None:
        return

    for planet_code, (orb_active, orb_peak) in ORB_VALUES.items():
        planet_id = connection.execute(
            sa.select(planets.c.id).where(
                planets.c.reference_version_id == reference_id,
                planets.c.code == planet_code,
            )
        ).scalar_one_or_none()
        if planet_id is None:
            continue

        connection.execute(
            sa.update(planet_profiles)
            .where(
                planet_profiles.c.planet_id == planet_id,
                planet_profiles.c.orb_active_deg == orb_active,
                planet_profiles.c.orb_peak_deg == orb_peak,
            )
            .values(
                orb_active_deg=None,
                orb_peak_deg=None,
            )
        )
