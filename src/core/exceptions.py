from typing import Any
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


class ProxyError(HTTPException):
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(status_code=status_code, detail=message)


class UnauthorizedError(HTTPException):
    def __init__(self, message: str = 'Unauthorized'):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)


class ForbiddenError(HTTPException):
    def __init__(self, message: str = 'Forbidden'):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=message)


class VaultConnectionError(ProxyError):
    def __init__(self, message: str = 'Vault connection failed'):
        super().__init__(message, status_code=503)


async def proxy_exception_handler(request: Request, exc: ProxyError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={'error': exc.detail}
    )


async def unauthorized_handler(request: Request, exc: UnauthorizedError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={'error': exc.detail}
    )


async def forbidden_handler(request: Request, exc: ForbiddenError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={'error': exc.detail}
    )
