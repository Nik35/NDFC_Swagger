# NDFC Source-of-Truth (SoT) — Complete Build Prompt (v2)

> **Purpose**: This prompt provides full context and instructions for an AI coding agent to build (or rebuild) the NDFC SoT application from scratch while adhering to the established "Golden State" architecture.
> **Date**: March 29, 2026

---

## 1. PROJECT IDENTITY & TECH STACK
*   **Name**: `ndfc-sot`
*   **Framework**: Python 3.11+ (FastAPI Async)
*   **Database**: PostgreSQL 16 (SQLAlchemy 2.0 Async + asyncpg)
*   **Migrations**: Alembic
*   **Purpose**: Centralized Source-of-Truth for Cisco NDFC VXLAN EVPN fabrics. Generates NAC-DC compatible YAML for Ansible deployment.

---

## 2. ARCHITECTURAL STANDARDS (MANDATORY)

### 2.1 Pydantic Model Strictness
*   **No Random Keys**: All models MUST set `model_config = {"extra": "forbid"}`.
*   **Documentation**: Every field MUST have `Field(description="...", examples=["..."])` for Swagger UI clarity.
*   **Discriminated Unions**: Interfaces must use the `Annotated[Union[...], Discriminator(...)]` pattern to handle multiple types (Access, Trunk, etc.).

### 2.2 Database & Service Patterns
*   **Single Interfaces Table**: All interface types live in one table with a `type` discriminator and a JSONB `type_config` column.
*   **Model Flattening**: The `InterfaceRead` model MUST use a `model_validator(mode="before")` to flatten `type_config` into top-level attributes for the API response.
*   **Mapping Aliases**:
    *   API `mode` maps to DB `type`.
    *   API `enabled` maps to DB `admin_state`.
*   **Upsert Logic**: Every service must implement an `upsert()` method using natural keys (e.g., `fabric_id` + `name`).

### 2.3 Error Handling
*   **Standardized 401**: Unauthorized requests return `{"detail": "...", "error_code": "UNAUTHORIZED"}`.
*   **Dependency Validation**: Use `app/validators/referential.py` to ensure hostnames/IDs exist before creation. Raise `NotFoundError` with `error_code: "DEPENDENCY_NOT_FOUND"`.

---

## 3. GOLDEN YAML BUILDER REQUIREMENTS

The `YamlBuilder` service must produce a nested dictionary matching these exact NDFC/Ansible expectations:

1.  **Nested Interfaces**: Interfaces are NOT top-level. They must be nested: `vxlan.topology.switches[].interfaces[]`.
2.  **Attach Groups**:
    *   **VRFs**: Switch attachments move to `vxlan.overlay.vrf_attach_groups`.
    *   **Networks**: Switch attachments move to `vxlan.overlay.network_attach_groups`.
    *   Groups named `<entity_name>_attach`.
3.  **Naming**: Inside attachments, the key MUST be `hostname` (not `name`).
4.  **Clean Output**: Omit entire sections (e.g., `policy`, `underlay`) if they are empty.

---

## 4. ENTITY & API MAP

| Resource | Base Path | DB Table |
| :--- | :--- | :--- |
| **Fabric** | `/api/v1/fabrics` | `fabrics` |
| **Switch** | `/api/v1/switches` | `switches` |
| **Interface** | `/api/v1/interfaces` | `interfaces` |
| **Network** | `/api/v1/networks` | `networks` |
| **VRF** | `/api/v1/vrfs` | `vrfs` |
| **Underlay** | `/api/v1/underlay` | `underlay_*` (8 tables) |
| **Import** | `/api/v1/import` | (Bulk upsert logic) |

---

## 5. REPRODUCTION STEPS (FOR AGENTS)

1.  **Phase 1 (Infra)**: Setup Docker Compose with Postgres 16. Implement API Key auth supporting comma-separated strings in `NDFC_SOT_API_KEY`.
2.  **Phase 2 (Models)**: Generate all SQLAlchemy models. Create Pydantic models with `extra="forbid"`.
3.  **Phase 3 (Services)**: Implement Services with `upsert` and referential validation.
4.  **Phase 4 (YAML)**: Implement `YamlBuilder` with the nesting and extraction logic defined in Section 3.
5.  **Phase 5 (Routers)**: Implement FastAPI routers using strict Pydantic types (avoid `dict` payloads).

---

## 6. CRITICAL FILE TEMPLATES

### InterfaceRead Flattening (app/models/interfaces/__init__.py)
```python
@model_validator(mode="before")
@classmethod
def _flatten_type_config(cls, data: any) -> any:
    if hasattr(data, "type_config") and isinstance(data.type_config, dict):
        res = {**data.__dict__}
        res.update(data.type_config)
        res["mode"] = data.type
        res["enabled"] = data.admin_state
        return res
    return data
```

### Dependency Validation (app/validators/referential.py)
```python
if not switch:
    raise NotFoundError(f"Switch '{hostname}' not found", error_code="DEPENDENCY_NOT_FOUND")
```
