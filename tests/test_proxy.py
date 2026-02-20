import pytest
from unittest.mock import AsyncMock, patch

from src.core.proxy import PondAPIProxy, get_pond_proxy
from src.core.exceptions import ProxyError


@pytest.mark.asyncio
class TestPondAPIProxy:
    async def test_cancel_lu_request_success(self, monkeypatch):
        proxy = PondAPIProxy()

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value={'status': 'ok'})
        mock_response.raise_for_status = lambda: None

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch.object(proxy, '_get_client', return_value=mock_client):
            result = await proxy.cancel_lu_request(
                iccid='1234567890123456789',
                token='test-token',
                request_id='test-req-id',
                version='2.1'
            )

            assert result == {'status': 'ok'}

        await proxy.close()

    async def test_cancel_lu_request_http_error(self, monkeypatch):
        proxy = PondAPIProxy()

        mock_response = AsyncMock()
        mock_response.status_code = 404
        mock_response.text = 'Not found'
        mock_response.raise_for_status.side_effect = Exception('404')

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch.object(proxy, '_get_client', return_value=mock_client):
            with pytest.raises(Exception):
                await proxy.cancel_lu_request(
                    iccid='1234567890123456789',
                    token='test-token',
                    request_id='test-req-id'
                )

        await proxy.close()
