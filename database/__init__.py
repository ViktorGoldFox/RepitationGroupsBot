from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_scoped_session, async_sessionmaker
from Core import config as core_settings

from asyncio import current_task

from database.models import Base

from logzero import logger

class db:
    def __init__(self):
        self.engine = create_async_engine(
            url=core_settings.db.url,
            echo=core_settings.db.echo
        )

        self.session_maker = async_sessionmaker(
            bind=self.engine,
            autoflush=core_settings.db.autoflush,
            expire_on_commit=core_settings.db.expire_on_commit
        )

    def get_scoped_session(self):
        session = async_scoped_session(
            session_factory=self.session_maker,
            scopefunc=current_task
        )

        return session

    async def close(self):
        await self.engine.dispose()

    async def on_startup(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(models.Base.metadata.create_all)

db_helper = db()