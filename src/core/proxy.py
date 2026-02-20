import logging
from typing import Any

import httpx
from fastapi import HTTPException

from src.config import settings
from src.core.exceptions import ProxyError

logger = logging.getLogger(__name__)


class PondAPIProxy:
    def __init__(self):
        self.base_url = settings.POND_API_BASE_URL
        self.timeout = settings.POND_API_TIMEOUT
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                follow_redirects=True
            )
        return self._client

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def cancel_lu_request(
        self,
        iccid: str,
        token: str,
        request_id: str,
        version: str = '2.1'
    ) -> dict[str, Any]:
        client = await self._get_client()

        path = f'/v{version}/network-access/cancel-lu-requests'
        params = {'iccid': iccid}

        headers = {
            'Authorization': f'Bearer {token}',
            'request-id': request_id,
            'version': version,
            'Content-Type': 'application/json'
        }

        try:
            response = await client.post(path, params=params, headers=headers)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error('Pond API error: %s - %s', e.response.status_code, e.response.text)
            raise ProxyError(
                f'Pond API error: {e.response.status_code}',
                status_code=e.response.status_code
            )

        except httpx.RequestError as e:
            logger.error('Request failed: %s', e)
            raise ProxyError('Failed to reach Pond API', status_code=503)

    async def health_check(self) -> bool:
        try:
            client = await self._get_client()
            response = await client.get('/health')
            return response.status_code == 200
        except Exception:
            return False


_pond_proxy = PondAPIProxy()


def get_pond_proxy() -> PondAPIProxy:
    return _pond_proxy
