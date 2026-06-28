from aiogram import Bot, Dispatcher
from logzero import logger

from bot.base.router import base_router
from bot.middlewares import LoggingMiddleware
from bot.repitation.router import repitation_router
from bot.rest.router import rest_router
from Core import config


class TelegramBot:
    def __init__(self, token: str):
        self.bot: Bot = Bot(token)
        self.dp = Dispatcher()

    def setup_handlers(self):
        self.dp.message.middleware(LoggingMiddleware())
        self.dp.include_router(base_router)
        self.dp.include_router(repitation_router)
        self.dp.include_router(rest_router)

    async def on_startup(self):
        logger.info("Registering routers and middlewares")
        self.setup_handlers()
        logger.info("Starting polling")
        await self.dp.start_polling(self.bot)

    async def on_shutdown(self):
        logger.info("Stopping bot")
        await self.bot.session.close()
        logger.info("Bot session closed")


bot = TelegramBot(config.bot.token)
