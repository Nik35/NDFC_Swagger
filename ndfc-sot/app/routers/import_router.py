"""NAC-DC import endpoints — full and per-entity."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_api_key
from app.database import get_db
from app.services.import_service import ImportService

router = APIRouter(
    prefix="/import",
    tags=["Import"],
    dependencies=[Depends(verify_api_key)],
)


@router.post(
    "/full",
    status_code=status.HTTP_201_CREATED,
    summary="Import a full NAC-DC vxlan structure",
)
async def import_full(payload: dict, db: AsyncSession = Depends(get_db)):
    svc = ImportService(db)
    counts = await svc.import_full(payload)
    return {"status": "ok", "counts": counts}


@router.post(
    "/switches/{fabric_name}",
    status_code=status.HTTP_201_CREATED,
    summary="Import switches into a fabric",
)
async def import_switches(
    fabric_name: str, items: list[dict], db: AsyncSession = Depends(get_db)
):
    svc = ImportService(db)
    count = await svc.import_switches(fabric_name, items)
    return {"status": "ok", "count": count}


@router.post(
    "/vrfs/{fabric_name}",
    status_code=status.HTTP_201_CREATED,
    summary="Import VRFs into a fabric",
)
async def import_vrfs(
    fabric_name: str, items: list[dict], db: AsyncSession = Depends(get_db)
):
    svc = ImportService(db)
    count = await svc.import_vrfs(fabric_name, items)
    return {"status": "ok", "count": count}


@router.post(
    "/networks/{fabric_name}",
    status_code=status.HTTP_201_CREATED,
    summary="Import networks into a fabric",
)
async def import_networks(
    fabric_name: str, items: list[dict], db: AsyncSession = Depends(get_db)
):
    svc = ImportService(db)
    count = await svc.import_networks(fabric_name, items)
    return {"status": "ok", "count": count}
