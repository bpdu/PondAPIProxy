from fastapi import APIRouter

from src.config import settings
from src.models.schemas import HealthResponse, ReadyResponse
from src.core.vault_client import get_vault_client
from src.core.ip_whitelist import get_whitelist

router = APIRouter(prefix='/health', tags=['health'])


@router.get('', response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        status='ok',
        version=settings.APP_VERSION
    )


@router.get('/ready', response_model=ReadyResponse)
async def ready() -> ReadyResponse:
    vault_client = get_vault_client()
    whitelist = get_whitelist()

    checks = {
        'tokens': True,
        'vault': vault_client.health_status(),
        'whitelist': len(whitelist._networks) > 0
    }

    return ReadyResponse(
        status='ready' if all(checks.values()) else 'degraded',
        checks=checks
    )
