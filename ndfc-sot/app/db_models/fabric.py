"""SQLAlchemy model for the ``fabrics`` table."""

from __future__ import annotations

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db_models.base import Base, UUIDTimestampMixin


class FabricDB(UUIDTimestampMixin, Base):
    __tablename__ = "fabrics"
    __table_args__ = (UniqueConstraint("name", name="uq_fabric_name"),)

    name: Mapped[str] = mapped_column(String(64), nullable=False)
    type: Mapped[str] = mapped_column(String(32), nullable=False)
