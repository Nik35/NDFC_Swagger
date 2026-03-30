"""Switch CRUD endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_api_key
from app.database import get_db
from app.models.inventory import SwitchCreate, SwitchRead, SwitchUpdate
from app.services.switch_service import SwitchService

router = APIRouter(
    prefix="/switches",
    tags=["Topology: Switches"],
    dependencies=[Depends(verify_api_key)],
)


@router.get(
    "/fabric/{fabric_id}",
    response_model=list[SwitchRead],
    summary="List switches in a fabric",
)
async def list_switches(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = SwitchService(db)
    return await svc.list_by_fabric(fabric_id)


@router.get(
    "/{switch_id}",
    response_model=SwitchRead,
    summary="Get a switch by ID",
)
async def get_switch(switch_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = SwitchService(db)
    return await svc.get_by_id(switch_id)


@router.post(
    "",
    response_model=SwitchRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a switch",
)
async def create_switch(payload: SwitchCreate, db: AsyncSession = Depends(get_db)):
    svc = SwitchService(db)
    row = await svc.create(payload)
    await db.commit()
    return row


@router.post(
    "/bulk",
    response_model=list[SwitchRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple switches",
)
async def create_switches_bulk(
    payloads: list[SwitchCreate], db: AsyncSession = Depends(get_db)
):
    svc = SwitchService(db)
    rows = await svc.create_bulk(payloads)
    await db.commit()
    return rows


@router.patch(
    "/{switch_id}",
    response_model=SwitchRead,
    summary="Update a switch",
)
async def update_switch(
    switch_id: UUID, payload: SwitchUpdate, db: AsyncSession = Depends(get_db)
):
    svc = SwitchService(db)
    row = await svc.update(switch_id, payload)
    await db.commit()
    return row


@router.delete(
    "/{switch_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a switch",
)
async def delete_switch(switch_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = SwitchService(db)
    await svc.delete(switch_id)
    await db.commit()
