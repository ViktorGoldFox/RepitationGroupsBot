from asyncio import current_task

from logzero import logger
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from Core import config as core_settings
from database.models import Base


class db:
    def __init__(self):
        logger.info("Creating database engine")
        self.engine = create_async_engine(
            url=core_settings.db.url, echo=core_settings.db.echo
        )

        self.session_maker = async_sessionmaker(
            bind=self.engine,
            autoflush=core_settings.db.autoflush,
            expire_on_commit=core_settings.db.expire_on_commit,
        )

    def get_scoped_session(self) -> AsyncSession:
        logger.debug("Creating scoped DB session")
        session = async_scoped_session(
            session_factory=self.session_maker, scopefunc=current_task
        )

        return session

    async def close(self):
        logger.info("Disposing database engine")
        await self.engine.dispose()

    async def on_startup(self):
        logger.info("Ensuring database schema exists")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


db_helper = db()
