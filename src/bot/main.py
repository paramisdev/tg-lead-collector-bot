import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import Settings
from bot.handlers import common, lead
from bot.middlewares.throttling import ThrottlingMiddleware


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    settings = Settings()
    bot = Bot(
        token=settings.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dispatcher = Dispatcher(storage=MemoryStorage())

    dispatcher["admin_chat_id"] = settings.admin_chat_id
    dispatcher.message.middleware(ThrottlingMiddleware())
    dispatcher.callback_query.middleware(ThrottlingMiddleware())

    dispatcher.include_router(common.router)
    dispatcher.include_router(lead.router)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


def run() -> None:
    asyncio.run(main())
