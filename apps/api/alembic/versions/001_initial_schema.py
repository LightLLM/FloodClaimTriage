"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2026-11-11

"""
from collections.abc import Sequence

import geoalchemy2
import sqlalchemy as sa

from alembic import op

revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create initial schema"""
    # Users table
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)

    # Properties table
    op.create_table(
        "properties",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("external_property_id", sa.Text(), nullable=False),
        sa.Column("geometry", geoalchemy2.types.Geometry("POINT", srid=4326), nullable=False),
        sa.Column("address_hash", sa.Text(), nullable=True),
        sa.Column("building_type", sa.Text(), nullable=True),
        sa.Column("exposure_value", sa.Numeric(18, 2), nullable=True),
        sa.Column("region", sa.Text(), nullable=True),
        sa.Column("data_source", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_property_id"),
    )
    op.create_index(
        op.f("ix_properties_external_property_id"),
        "properties",
        ["external_property_id"],
        unique=False,
    )
    op.create_index(
        "idx_properties_geometry",
        "properties",
        ["geometry"],
        unique=False,
        postgresql_using="gist",
    )

    # Events table
    op.create_table(
        "events",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("geometry", geoalchemy2.types.Geometry("GEOMETRY", srid=4326), nullable=True),
        sa.Column("stac_collection_id", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Observations table
    op.create_table(
        "observations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("property_id", sa.UUID(), nullable=False),
        sa.Column("event_id", sa.UUID(), nullable=False),
        sa.Column("observation_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("flood_extent", sa.Boolean(), nullable=True),
        sa.Column("distance_to_flood_m", sa.Numeric(), nullable=True),
        sa.Column("rainfall_percentile", sa.Numeric(), nullable=True),
        sa.Column("river_stage_exceedance", sa.Boolean(), nullable=True),
        sa.Column("elevation_m", sa.Numeric(), nullable=True),
        sa.Column("optical_change", sa.Numeric(), nullable=True),
        sa.Column("cloud_quality", sa.Numeric(), nullable=True),
        sa.Column("sensor_source", sa.Text(), nullable=True),
        sa.Column("feature_payload", sa.dialects.postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["property_id"], ["properties.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_observations_property_id"), "observations", ["property_id"], unique=False
    )
    op.create_index(op.f("ix_observations_event_id"), "observations", ["event_id"], unique=False)

    # Scores table
    op.create_table(
        "scores",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("property_id", sa.UUID(), nullable=False),
        sa.Column("event_id", sa.UUID(), nullable=False),
        sa.Column("model_version", sa.Text(), nullable=False),
        sa.Column("damage_probability", sa.Numeric(5, 4), nullable=False),
        sa.Column("damage_confidence", sa.Text(), nullable=False),
        sa.Column("inspection_priority", sa.String(10), nullable=False),
        sa.Column("recommended_action", sa.Text(), nullable=False),
        sa.Column("evidence", sa.dialects.postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["property_id"], ["properties.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_scores_property_id"), "scores", ["property_id"], unique=False)
    op.create_index(op.f("ix_scores_event_id"), "scores", ["event_id"], unique=False)
    op.create_index(
        op.f("ix_scores_inspection_priority"), "scores", ["inspection_priority"], unique=False
    )
    op.create_index(
        "idx_scores_event_priority",
        "scores",
        ["event_id", "inspection_priority", sa.text("damage_probability DESC")],
        unique=False,
    )

    # Audit events table
    op.create_table(
        "audit_events",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("property_id", sa.UUID(), nullable=True),
        sa.Column("event_id", sa.UUID(), nullable=True),
        sa.Column("score_id", sa.UUID(), nullable=True),
        sa.Column("action", sa.Text(), nullable=False),
        sa.Column("before_value", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("after_value", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_events_action"), "audit_events", ["action"], unique=False)
    op.create_index(
        op.f("ix_audit_events_created_at"), "audit_events", ["created_at"], unique=False
    )


def downgrade() -> None:
    """Drop all tables"""
    op.drop_table("audit_events")
    op.drop_table("scores")
    op.drop_table("observations")
    op.drop_table("events")
    op.drop_table("properties")
    op.drop_table("users")
