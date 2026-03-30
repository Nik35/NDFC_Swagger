"""Route Control CRUD endpoints — 10 entity types."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_api_key
from app.database import get_db
from app.services.route_control_service import (
    Ipv4PrefixListService,
    Ipv6PrefixListService,
    StandardCommunityListService,
    ExtendedCommunityListService,
    IpAsPathAccessListService,
    RouteMapService,
    IpAclService,
    MacListService,
    ObjectGroupService,
    TimeRangeService,
)

router = APIRouter(
    prefix="/route-control",
    tags=["Route Control"],
    dependencies=[Depends(verify_api_key)],
)


# ═══════════════════════════════════════════════════════════
# Generic helpers — each entity type follows the same pattern
# ═══════════════════════════════════════════════════════════

def _crud_routes(sub_prefix: str, svc_cls: type):
    """Register list / get / create / create_bulk / update / delete for one RC entity."""

    @router.get(
        f"/{sub_prefix}/fabric/{{fabric_id}}",
        summary=f"List {sub_prefix}",
    )
    async def list_entities(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
        return await svc_cls(db).list_by_fabric(fabric_id)

    @router.get(
        f"/{sub_prefix}/{{entity_id}}",
        summary=f"Get a {sub_prefix} by ID",
    )
    async def get_entity(entity_id: UUID, db: AsyncSession = Depends(get_db)):
        return await svc_cls(db).get_by_id(entity_id)

    @router.post(
        f"/{sub_prefix}",
        status_code=status.HTTP_201_CREATED,
        summary=f"Create a {sub_prefix}",
    )
    async def create_entity(payload: dict, db: AsyncSession = Depends(get_db)):
        row = await svc_cls(db).create(payload)
        await db.commit()
        return row

    @router.post(
        f"/{sub_prefix}/bulk",
        status_code=status.HTTP_201_CREATED,
        summary=f"Create multiple {sub_prefix}",
    )
    async def create_bulk(payloads: list[dict], db: AsyncSession = Depends(get_db)):
        rows = await svc_cls(db).create_bulk(payloads)
        await db.commit()
        return rows

    @router.patch(
        f"/{sub_prefix}/{{entity_id}}",
        summary=f"Update a {sub_prefix}",
    )
    async def update_entity(
        entity_id: UUID, payload: dict, db: AsyncSession = Depends(get_db)
    ):
        row = await svc_cls(db).update(entity_id, payload)
        await db.commit()
        return row

    @router.delete(
        f"/{sub_prefix}/{{entity_id}}",
        status_code=status.HTTP_204_NO_CONTENT,
        summary=f"Delete a {sub_prefix}",
    )
    async def delete_entity(entity_id: UUID, db: AsyncSession = Depends(get_db)):
        await svc_cls(db).delete(entity_id)
        await db.commit()

    # Give each function a unique name so FastAPI doesn't complain
    for fn in (list_entities, get_entity, create_entity, create_bulk, update_entity, delete_entity):
        fn.__name__ = f"{fn.__name__}_{sub_prefix.replace('-', '_')}"
        fn.__qualname__ = fn.__name__


_crud_routes("ipv4-prefix-lists", Ipv4PrefixListService)
_crud_routes("ipv6-prefix-lists", Ipv6PrefixListService)
_crud_routes("standard-community-lists", StandardCommunityListService)
_crud_routes("extended-community-lists", ExtendedCommunityListService)
_crud_routes("as-path-lists", IpAsPathAccessListService)
_crud_routes("route-maps", RouteMapService)
_crud_routes("ip-acls", IpAclService)
_crud_routes("mac-lists", MacListService)
_crud_routes("object-groups", ObjectGroupService)
_crud_routes("time-ranges", TimeRangeService)
