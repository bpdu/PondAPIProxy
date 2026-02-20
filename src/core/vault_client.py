import logging
from hvac import Client
from hvac.exceptions import VaultError

from src.config import settings
from src.core.exceptions import VaultConnectionError

logger = logging.getLogger(__name__)


class VaultClient:
    def __init__(self):
        self.client = Client(
            url=settings.VAULT_ADDR,
            token=settings.VAULT_TOKEN
        )
        self._kv_version = 2
        self._mount_point = 'secret'

    def check_connection(self) -> bool:
        try:
            return self.client.is_authenticated()
        except VaultError as e:
            logger.error('Vault connection failed: %s', e)
            return False

    def get_pond_token(self) -> str | None:
        try:
            path = f'{settings.VAULT_KV_PATH}/{settings.VAULT_TOKEN_FIELD}'

            if self._kv_version == 2:
                response = self.client.secrets.kv.v2.read_secret_version(
                    path=settings.VAULT_KV_PATH,
                    mount_point=self._mount_point
                )
                return response['data']['data'].get(settings.VAULT_TOKEN_FIELD)
            else:
                response = self.client.secrets.kv.v1.read_secret(
                    path=settings.VAULT_KV_PATH,
                    mount_point=self._mount_point
                )
                return response.get('data', {}).get(settings.VAULT_TOKEN_FIELD)

        except VaultError as e:
            logger.error('Failed to get Pond token from Vault: %s', e)
            raise VaultConnectionError('Failed to retrieve API token')

    def health_status(self) -> bool:
        return self.check_connection()


_vault_client = VaultClient()


def get_vault_client() -> VaultClient:
    return _vault_client
