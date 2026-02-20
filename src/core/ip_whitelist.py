from ipaddress import IPv4Network, IPv6Network, ip_address, ip_network
from pathlib import Path

from fastapi import HTTPException, Request

from src.config import settings
from src.core.exceptions import ForbiddenError


class IPWhitelist:
    def __init__(self, path: str | None = None):
        self.path = path or settings.IP_WHITELIST_PATH
        self._networks: list[IPv4Network | IPv6Network] = []
        self._load()

    def _load(self) -> None:
        self._networks = []

        whitelist_path = Path(self.path)
        if not whitelist_path.exists():
            return

        for line in whitelist_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            try:
                network = ip_network(line, strict=False)
                self._networks.append(network)
            except ValueError:
                continue

    def is_allowed(self, ip: str) -> bool:
        if not self._networks:
            return True

        try:
            addr = ip_address(ip)
            return any(addr in net for net in self._networks)
        except ValueError:
            return False

    def reload(self) -> None:
        self._load()


_whitelist = IPWhitelist()


def get_whitelist() -> IPWhitelist:
    return _whitelist


async def require_whitelisted_ip(request: Request) -> str:
    client_ip = request.client.host if request.client else '0.0.0.0'

    whitelist = get_whitelist()
    if not whitelist.is_allowed(client_ip):
        raise ForbiddenError(f'IP {client_ip} not whitelisted')

    return client_ip
