import asyncio
from datetime import datetime

from aiogram import Dispatcher, Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage


from config import config
from handlers import handlers
from middlewares.middlewares import ThrottlingMiddleware

async def main():
    bot = Bot(token=config.BOT_TOKEN.get_secret_value(), 
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.message.middleware.register(ThrottlingMiddleware(storage=storage))
    dp["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f'Started at {dp["started_at"]}')
    dp.include_routers(handlers.router, handlers.state_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')