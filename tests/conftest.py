import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport

from src.main import app
from src.config import settings
from src.core.ip_whitelist import IPWhitelist, get_whitelist
from src.core.vault_client import VaultClient, get_vault_client


@pytest.fixture
def transport():
    return ASGITransport(app=app)


@pytest.fixture
def client(transport):
    from httpx import AsyncClient
    import asyncio

    async def _client():
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

    return _client


@pytest.fixture
def test_token():
    return 'test-token-123'


@pytest.fixture
def mock_whitelist():
    whitelist = IPWhitelist()
    whitelist._networks = []
    yield whitelist
    whitelist._networks = []


@pytest.fixture
def mock_vault():
    class MockVaultClient:
        def __init__(self):
            self.token = 'mock-pond-token'

        def check_connection(self):
            return True

        def get_pond_token(self):
            return self.token

        def health_status(self):
            return True

    original = get_vault_client
    import src.core.vault_client
    import src.dependencies

    src.core.vault_client._vault_client = MockVaultClient()
    src.dependencies._vault_client = MockVaultClient()

    yield MockVaultClient()

    src.core.vault_client._vault_client = original()
