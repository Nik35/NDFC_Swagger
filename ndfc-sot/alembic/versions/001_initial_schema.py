"""Initial schema creation.

Revision ID: 001_initial
Revises: 
Create Date: 2026-03-25
"""

from __future__ import annotations

from alembic import op

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all tables via metadata.create_all."""
    from app.db_models import Base  # noqa: F401
    from sqlalchemy import inspect

    bind = op.get_bind()
    inspector = inspect(bind)
    existing = inspector.get_table_names()

    if "fabrics" not in existing:
        Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    """Drop all tables."""
    from app.db_models import Base

    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)