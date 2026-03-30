"""Global config CRUD endpoints — 1:1 per fabric."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_api_key
from app.database import get_db
from app.models.global_config import GlobalConfigCreate, GlobalConfigRead, GlobalConfigUpdate
from app.services.global_service import GlobalService

router = APIRouter(
    prefix="/globals",
    tags=["Global"],
    dependencies=[Depends(verify_api_key)],
)


@router.get(
    "/fabric/{fabric_id}",
    response_model=GlobalConfigRead,
    summary="Get global config for a fabric",
)
async def get_global(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = GlobalService(db)
    return await svc.get_by_fabric(fabric_id)


@router.put(
    "/fabric/{fabric_id}",
    response_model=GlobalConfigRead,
    summary="Create or update global config for a fabric",
)
async def upsert_global(
    fabric_id: UUID, payload: GlobalConfigUpdate, db: AsyncSession = Depends(get_db)
):
    svc = GlobalService(db)
    data = payload.model_dump(exclude_unset=True)
    data["fabric_id"] = fabric_id
    row = await svc.upsert(fabric_id, data)
    await db.commit()
    return row


@router.delete(
    "/fabric/{fabric_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete global config for a fabric",
)
async def delete_global(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = GlobalService(db)
    await svc.delete(fabric_id)
    await db.commit()
