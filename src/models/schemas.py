from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    version: str


class ReadyResponse(BaseModel):
    status: str
    checks: dict[str, bool]


class CancelLuRequest(BaseModel):
    iccid: str = Field(..., min_length=1, max_length=30)


class PondErrorResponse(BaseModel):
    error: str
    message: str | None = None
    status_code: int | None = None
