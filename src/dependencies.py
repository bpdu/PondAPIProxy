from fastapi import Depends, Header

from src.core.ip_whitelist import require_whitelisted_ip
from src.core.security import require_valid_token
from src.core.vault_client import get_vault_client


async def get_pond_api_token(
    auth_token: str = Depends(require_valid_token)
) -> str:
    vault_client = get_vault_client()

    if not vault_client.health_status():
        from src.core.exceptions import VaultConnectionError
        raise VaultConnectionError('Vault is unavailable')

    token = vault_client.get_pond_token()
    if not token:
        from src.core.exceptions import VaultConnectionError
        raise VaultConnectionError('Pond API token not found in Vault')

    return token


async def authenticated_proxy(
    ip: str = Depends(require_whitelisted_ip),
    token: str = Depends(require_valid_token),
    pond_token: str = Depends(get_pond_api_token)
) -> tuple[str, str, str]:
    return ip, token, pond_token
