from fastapi import Header, HTTPException, status

from src.config import settings
from src.core.exceptions import UnauthorizedError


def extract_bearer_token(authorization: str | None = Header(None)) -> str:
    if not authorization:
        raise UnauthorizedError('Missing Authorization header')

    if not authorization.startswith('Bearer '):
        raise UnauthorizedError('Invalid Authorization header format')

    token = authorization.removeprefix('Bearer ').strip()
    if not token:
        raise UnauthorizedError('Empty token')

    return token


def validate_token(token: str) -> bool:
    return token in settings.tokens


async def require_valid_token(authorization: str | None = Header(None)) -> str:
    token = extract_bearer_token(authorization)

    if not validate_token(token):
        raise UnauthorizedError('Invalid token')

    return token
