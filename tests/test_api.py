import pytest
from httpx import AsyncClient, ASGITransport

from src.main import app
from src.config import settings


@pytest.mark.asyncio
class TestHealthEndpoints:
    async def test_health_endpoint(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            response = await ac.get('/health')

            assert response.status_code == 200
            data = response.json()
            assert data['status'] == 'ok'
            assert 'version' in data

    async def test_ready_endpoint(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            response = await ac.get('/health/ready')

            assert response.status_code == 200
            data = response.json()
            assert 'status' in data
            assert 'checks' in data
            assert isinstance(data['checks'], dict)


@pytest.mark.asyncio
class TestProxyEndpoint:
    async def test_proxy_missing_auth_header(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            response = await ac.post(
                '/proxy/v2.1/network-access/cancel-lu-requests',
                params={'iccid': '1234567890123456789'}
            )

            assert response.status_code == 401

    async def test_proxy_invalid_token_format(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            response = await ac.post(
                '/proxy/v2.1/network-access/cancel-lu-requests',
                params={'iccid': '1234567890123456789'},
                headers={'Authorization': 'Basic invalid'}
            )

            assert response.status_code == 401

    async def test_proxy_missing_request_id_header(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            response = await ac.post(
                '/proxy/v2.1/network-access/cancel-lu-requests',
                params={'iccid': '1234567890123456789'},
                headers={'Authorization': 'Bearer test-token'}
            )

            assert response.status_code == 422
