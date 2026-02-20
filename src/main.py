import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.config import settings
from src.api import health, routes
from src.core.exceptions import (
    ProxyError,
    UnauthorizedError,
    ForbiddenError,
    VaultConnectionError,
    proxy_exception_handler,
    unauthorized_handler,
    forbidden_handler
)
from src.core.proxy import get_pond_proxy

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('Starting Pond API Proxy v%s', settings.APP_VERSION)
    yield
    proxy = get_pond_proxy()
    await proxy.close()
    logger.info('Pond API Proxy stopped')


app = FastAPI(
    title='Pond API Proxy',
    version=settings.APP_VERSION,
    lifespan=lifespan
)

app.add_exception_handler(ProxyError, proxy_exception_handler)
app.add_exception_handler(UnauthorizedError, unauthorized_handler)
app.add_exception_handler(ForbiddenError, forbidden_handler)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={'error': 'validation_error', 'details': exc.errors()}
    )


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    logger.exception('Unhandled exception: %s', exc)
    return JSONResponse(
        status_code=500,
        content={'error': 'internal_error', 'message': 'Internal server error'}
    )


app.include_router(health.router)
app.include_router(routes.router)


@app.middleware('http')
async def log_requests(request: Request, call_next):
    logger.info('%s %s', request.method, request.url.path)
    response = await call_next(request)
    logger.info('%s %s - %s', request.method, request.url.path, response.status_code)
    return response


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        'main:app',
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
