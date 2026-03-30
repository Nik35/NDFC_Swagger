"""Underlay CRUD endpoints — 8 sub-sections, each 1:1 per fabric."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_api_key
from app.database import get_db
from app.models.underlay import (
    UnderlayGeneralRead, UnderlayGeneralUpdate,
    UnderlayIpv4Read, UnderlayIpv4Update,
    UnderlayIpv6Read, UnderlayIpv6Update,
    UnderlayIsisRead, UnderlayIsisUpdate,
    UnderlayOspfRead, UnderlayOspfUpdate,
    UnderlayBgpRead, UnderlayBgpUpdate,
    UnderlayBfdRead, UnderlayBfdUpdate,
    UnderlayMulticastRead, UnderlayMulticastUpdate
)
from app.services.underlay_service import (
    UnderlayGeneralService,
    UnderlayIpv4Service,
    UnderlayIpv6Service,
    UnderlayIsisService,
    UnderlayOspfService,
    UnderlayBgpService,
    UnderlayBfdService,
    UnderlayMulticastService,
)

router = APIRouter(
    prefix="/underlay",
    tags=["Underlay"],
    dependencies=[Depends(verify_api_key)],
)


# ── General ───────────────────────────────────────────────────────────

@router.get("/general/fabric/{fabric_id}", response_model=UnderlayGeneralRead, summary="Get underlay general config")
async def get_general(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    return await UnderlayGeneralService(db).get_by_fabric(fabric_id)


@router.put("/general/fabric/{fabric_id}", response_model=UnderlayGeneralRead, summary="Upsert underlay general config")
async def upsert_general(
    fabric_id: UUID, payload: UnderlayGeneralUpdate, db: AsyncSession = Depends(get_db)
):
    svc = UnderlayGeneralService(db)
    row = await svc.upsert(fabric_id, payload.model_dump(exclude_unset=True))
    await db.commit()
    return row


@router.delete(
    "/general/fabric/{fabric_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete underlay general config",
)
async def delete_general(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    await UnderlayGeneralService(db).delete(fabric_id)
    await db.commit()


# ── IPv4 ──────────────────────────────────────────────────────────────

@router.get("/ipv4/fabric/{fabric_id}", response_model=UnderlayIpv4Read, summary="Get underlay IPv4 config")
async def get_ipv4(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    return await UnderlayIpv4Service(db).get_by_fabric(fabric_id)


@router.put("/ipv4/fabric/{fabric_id}", response_model=UnderlayIpv4Read, summary="Upsert underlay IPv4 config")
async def upsert_ipv4(
    fabric_id: UUID, payload: UnderlayIpv4Update, db: AsyncSession = Depends(get_db)
):
    svc = UnderlayIpv4Service(db)
    row = await svc.upsert(fabric_id, payload.model_dump(exclude_unset=True))
    await db.commit()
    return row


@router.delete(
    "/ipv4/fabric/{fabric_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete underlay IPv4 config",
)
async def delete_ipv4(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    await UnderlayIpv4Service(db).delete(fabric_id)
    await db.commit()


# ── IPv6 ──────────────────────────────────────────────────────────────

@router.get("/ipv6/fabric/{fabric_id}", response_model=UnderlayIpv6Read, summary="Get underlay IPv6 config")
async def get_ipv6(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    return await UnderlayIpv6Service(db).get_by_fabric(fabric_id)


@router.put("/ipv6/fabric/{fabric_id}", response_model=UnderlayIpv6Read, summary="Upsert underlay IPv6 config")
async def upsert_ipv6(
    fabric_id: UUID, payload: UnderlayIpv6Update, db: AsyncSession = Depends(get_db)
):
    svc = UnderlayIpv6Service(db)
    row = await svc.upsert(fabric_id, payload.model_dump(exclude_unset=True))
    await db.commit()
    return row


@router.delete(
    "/ipv6/fabric/{fabric_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete underlay IPv6 config",
)
async def delete_ipv6(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    await UnderlayIpv6Service(db).delete(fabric_id)
    await db.commit()


# ── IS-IS ─────────────────────────────────────────────────────────────

@router.get("/isis/fabric/{fabric_id}", response_model=UnderlayIsisRead, summary="Get underlay IS-IS config")
async def get_isis(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    return await UnderlayIsisService(db).get_by_fabric(fabric_id)


@router.put("/isis/fabric/{fabric_id}", response_model=UnderlayIsisRead, summary="Upsert underlay IS-IS config")
async def upsert_isis(
    fabric_id: UUID, payload: UnderlayIsisUpdate, db: AsyncSession = Depends(get_db)
):
    svc = UnderlayIsisService(db)
    row = await svc.upsert(fabric_id, payload.model_dump(exclude_unset=True))
    await db.commit()
    return row


@router.delete(
    "/isis/fabric/{fabric_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete underlay IS-IS config",
)
async def delete_isis(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    await UnderlayIsisService(db).delete(fabric_id)
    await db.commit()


# ── OSPF ──────────────────────────────────────────────────────────────

@router.get("/ospf/fabric/{fabric_id}", response_model=UnderlayOspfRead, summary="Get underlay OSPF config")
async def get_ospf(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    return await UnderlayOspfService(db).get_by_fabric(fabric_id)


@router.put("/ospf/fabric/{fabric_id}", response_model=UnderlayOspfRead, summary="Upsert underlay OSPF config")
async def upsert_ospf(
    fabric_id: UUID, payload: UnderlayOspfUpdate, db: AsyncSession = Depends(get_db)
):
    svc = UnderlayOspfService(db)
    row = await svc.upsert(fabric_id, payload.model_dump(exclude_unset=True))
    await db.commit()
    return row


@router.delete(
    "/ospf/fabric/{fabric_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete underlay OSPF config",
)
async def delete_ospf(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    await UnderlayOspfService(db).delete(fabric_id)
    await db.commit()


# ── BGP ───────────────────────────────────────────────────────────────

@router.get("/bgp/fabric/{fabric_id}", response_model=UnderlayBgpRead, summary="Get underlay BGP config")
async def get_bgp(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    return await UnderlayBgpService(db).get_by_fabric(fabric_id)


@router.put("/bgp/fabric/{fabric_id}", response_model=UnderlayBgpRead, summary="Upsert underlay BGP config")
async def upsert_bgp(
    fabric_id: UUID, payload: UnderlayBgpUpdate, db: AsyncSession = Depends(get_db)
):
    svc = UnderlayBgpService(db)
    row = await svc.upsert(fabric_id, payload.model_dump(exclude_unset=True))
    await db.commit()
    return row


@router.delete(
    "/bgp/fabric/{fabric_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete underlay BGP config",
)
async def delete_bgp(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    await UnderlayBgpService(db).delete(fabric_id)
    await db.commit()


# ── BFD ───────────────────────────────────────────────────────────────

@router.get("/bfd/fabric/{fabric_id}", response_model=UnderlayBfdRead, summary="Get underlay BFD config")
async def get_bfd(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    return await UnderlayBfdService(db).get_by_fabric(fabric_id)


@router.put("/bfd/fabric/{fabric_id}", response_model=UnderlayBfdRead, summary="Upsert underlay BFD config")
async def upsert_bfd(
    fabric_id: UUID, payload: UnderlayBfdUpdate, db: AsyncSession = Depends(get_db)
):
    svc = UnderlayBfdService(db)
    row = await svc.upsert(fabric_id, payload.model_dump(exclude_unset=True))
    await db.commit()
    return row


@router.delete(
    "/bfd/fabric/{fabric_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete underlay BFD config",
)
async def delete_bfd(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    await UnderlayBfdService(db).delete(fabric_id)
    await db.commit()


# ── Multicast ─────────────────────────────────────────────────────────

@router.get("/multicast/fabric/{fabric_id}", response_model=UnderlayMulticastRead, summary="Get underlay multicast config")
async def get_multicast(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    return await UnderlayMulticastService(db).get_by_fabric(fabric_id)


@router.put("/multicast/fabric/{fabric_id}", response_model=UnderlayMulticastRead, summary="Upsert underlay multicast config")
async def upsert_multicast(
    fabric_id: UUID, payload: UnderlayMulticastUpdate, db: AsyncSession = Depends(get_db)
):
    svc = UnderlayMulticastService(db)
    row = await svc.upsert(fabric_id, payload.model_dump(exclude_unset=True))
    await db.commit()
    return row


@router.delete(
    "/multicast/fabric/{fabric_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete underlay multicast config",
)
async def delete_multicast(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    await UnderlayMulticastService(db).delete(fabric_id)
    await db.commit()
