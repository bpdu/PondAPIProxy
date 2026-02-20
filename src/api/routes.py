import logging
from typing import Any
from fastapi import APIRouter, Depends, Header, Query
from fastapi.responses import JSONResponse

from src.config import settings
from src.core.proxy import get_pond_proxy
from src.dependencies import authenticated_proxy
from src.models.schemas import PondErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/proxy', tags=['proxy'])


@router.post('/v{version:path}/network-access/cancel-lu-requests')
async def cancel_lu_request(
    iccid: str = Query(..., min_length=1, max_length=30),
    version: str = Query(..., pattern=r'^\d+\.\d+$'),
    request_id: str = Header(..., alias='request-id'),
    auth: tuple[str, str, str] = Depends(authenticated_proxy)
) -> JSONResponse:
    client_ip, auth_token, pond_token = auth
    proxy = get_pond_proxy()

    logger.info(
        'Cancel LU request: iccid=%s, version=%s, request_id=%s, ip=%s',
        iccid, version, request_id, client_ip
    )

    try:
        result = await proxy.cancel_lu_request(
            iccid=iccid,
            token=pond_token,
            request_id=request_id,
            version=version
        )
        return JSONResponse(content=result, status_code=200)

    except Exception as e:
        logger.error('Proxy error: %s', e)
        error_response = PondErrorResponse(
            error='proxy_error',
            message=str(e),
            status_code=500
        )
        return JSONResponse(content=error_response.model_dump(), status_code=500)
