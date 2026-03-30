"""Fabric CRUD endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_api_key
from app.database import get_db
from app.models.fabric import FabricCreate, FabricRead, FabricUpdate
from app.services.fabric_service import FabricService

router = APIRouter(
    prefix="/fabrics",
    tags=["Fabrics"],
    dependencies=[Depends(verify_api_key)],
)


@router.get(
    "",
    response_model=list[FabricRead],
    summary="List all fabrics",
)
async def list_fabrics(db: AsyncSession = Depends(get_db)):
    svc = FabricService(db)
    return await svc.list_all()


@router.get(
    "/{fabric_id}",
    response_model=FabricRead,
    summary="Get a fabric by ID",
)
async def get_fabric(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = FabricService(db)
    return await svc.get_by_id(fabric_id)


@router.post(
    "",
    response_model=FabricRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a fabric",
)
async def create_fabric(payload: FabricCreate, db: AsyncSession = Depends(get_db)):
    svc = FabricService(db)
    row = await svc.create(payload)
    await db.commit()
    return row


@router.post(
    "/bulk",
    response_model=list[FabricRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple fabrics",
)
async def create_fabrics_bulk(
    payloads: list[FabricCreate], db: AsyncSession = Depends(get_db)
):
    svc = FabricService(db)
    rows = await svc.create_bulk(payloads)
    await db.commit()
    return rows


@router.patch(
    "/{fabric_id}",
    response_model=FabricRead,
    summary="Update a fabric",
)
async def update_fabric(
    fabric_id: UUID, payload: FabricUpdate, db: AsyncSession = Depends(get_db)
):
    svc = FabricService(db)
    row = await svc.update(fabric_id, payload)
    await db.commit()
    return row


@router.delete(
    "/{fabric_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a fabric",
)
async def delete_fabric(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = FabricService(db)
    await svc.delete(fabric_id)
    await db.commit()
