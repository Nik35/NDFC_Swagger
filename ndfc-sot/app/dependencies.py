"""Shared FastAPI dependencies."""

from __future__ import annotations

from uuid import UUID

from fastapi import Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.db_models.fabric import FabricDB
from app.exceptions import NotFoundError


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------

class PaginationParams:
    """Standard pagination query parameters."""

    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size


# ---------------------------------------------------------------------------
# Fabric resolution
# ---------------------------------------------------------------------------

async def get_fabric_by_name(
    fabric_name: str,
    db: AsyncSession = Depends(get_db),
) -> FabricDB:
    """Resolve *fabric_name* path parameter to a ``FabricDB`` row.

    Raises ``NotFoundError`` when the fabric does not exist.
    """
    result = await db.execute(select(FabricDB).where(FabricDB.name == fabric_name))
    fabric = result.scalar_one_or_none()
    if fabric is None:
        raise NotFoundError(f"Fabric '{fabric_name}' not found")
    return fabric


async def get_fabric_id_by_name(
    fabric_name: str,
    db: AsyncSession = Depends(get_db),
) -> UUID:
    """Convenience wrapper that returns only the fabric UUID."""
    fabric = await get_fabric_by_name(fabric_name, db)
    return fabric.id