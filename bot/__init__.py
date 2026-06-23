from aiogram import Bot, Dispatcher, types

from bot.base.router import base_router
from bot.repitation.router import repitation_router
from Core import config


class TelegramBot:
    def __init__(self, token: str):
        self.bot: Bot = Bot(token)
        self.dp = Dispatcher()

    def setup_handlers(self):
        self.dp.include_router(base_router)
        self.dp.include_router(repitation_router)

    async def on_startup(self):
        self.setup_handlers()
        await self.dp.start_polling(self.bot)


bot = TelegramBot(config.bot.token)
