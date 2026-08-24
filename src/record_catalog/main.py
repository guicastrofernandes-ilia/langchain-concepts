from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

from record_catalog.database import Base, get_engine
from record_catalog.router import router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Record Catalog API", lifespan=lifespan)

    @app.exception_handler(OperationalError)
    async def db_unavailable_handler(request: Request, exc: OperationalError) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={"detail": "Database unavailable"},
        )

    app.include_router(router)
    return app
