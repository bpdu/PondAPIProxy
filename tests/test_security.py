import pytest
from fastapi import Header

from src.core.security import extract_bearer_token, validate_token, require_valid_token
from src.core.exceptions import UnauthorizedError
from src.config import settings


class TestBearerToken:
    def test_extract_valid_token(self):
        token = extract_bearer_token('Bearer my-token-123')
        assert token == 'my-token-123'

    def test_extract_token_with_spaces(self):
        token = extract_bearer_token('Bearer   my-token-123   ')
        assert token == 'my-token-123'

    def test_extract_missing_header(self):
        with pytest.raises(UnauthorizedError):
            extract_bearer_token(None)

    def test_extract_invalid_format(self):
        with pytest.raises(UnauthorizedError):
            extract_bearer_token('Basic my-token')

    def test_extract_empty_token(self):
        with pytest.raises(UnauthorizedError):
            extract_bearer_token('Bearer   ')

    def test_validate_token(self, monkeypatch):
        monkeypatch.setenv('ALLOWED_TOKENS', 'token1,token2,token3')
        settings.model_rebuild()

        assert validate_token('token1') is True
        assert validate_token('token2') is True
        assert validate_token('invalid') is False


class TestIPWhitelist:
    def test_empty_whitelist_allows_all(self, mock_whitelist):
        assert mock_whitelist.is_allowed('192.168.1.1') is True
        assert mock_whitelist.is_allowed('8.8.8.8') is True

    def test_cidr_whitelist(self, mock_whitelist):
        mock_whitelist._networks = []
        from ipaddress import ip_network
        mock_whitelist._networks.append(ip_network('192.168.1.0/24'))

        assert mock_whitelist.is_allowed('192.168.1.100') is True
        assert mock_whitelist.is_allowed('192.168.2.100') is False

    def test_ipv6_whitelist(self, mock_whitelist):
        mock_whitelist._networks = []
        from ipaddress import ip_network
        mock_whitelist._networks.append(ip_network('::1/128'))

        assert mock_whitelist.is_allowed('::1') is True
        assert mock_whitelist.is_allowed('2001:db8::1') is False
