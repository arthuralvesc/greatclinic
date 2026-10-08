from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.v1.routers.patients import router as patients_router
from app.core.access_log import AccessLogMiddleware, configure_access_logging
from app.core.config import Settings
from app.core.errors import register_exception_handlers
from app.core.request_id import RequestIdMiddleware
from app.core.security import verify_api_key


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    engine = create_async_engine(settings.database_url)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        await engine.dispose()

    app = FastAPI(title="GreatClinic", lifespan=lifespan)
    app.state.settings = settings
    app.state.session_factory = async_sessionmaker(engine, expire_on_commit=False)
    configure_access_logging()
    # The last middleware added is the outermost: request id must wrap the access log.
    app.add_middleware(AccessLogMiddleware)
    app.add_middleware(RequestIdMiddleware)
    register_exception_handlers(app)
    app.include_router(patients_router, dependencies=[Depends(verify_api_key)])
    return app
