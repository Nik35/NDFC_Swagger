"""API Key authentication."""

from fastapi import Header, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(
    api_key: str = Security(api_key_header),
):
    """Validate the X-API-Key header against the configured key list.

    The ``NDFC_SOT_API_KEY`` env var accepts a single key or a
    comma-separated list (e.g. ``KEY1,KEY2``).
    """
    if not api_key or api_key not in settings.API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "detail": "Invalid or missing API key",
                "error_code": "UNAUTHORIZED",
            },
        )
    return api_key
