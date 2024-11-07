import time

from aiogram import BaseMiddleware, Bot
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage

from typing import Callable, Dict, Any, Awaitable

from config import config

bot = Bot(token=config.BOT_TOKEN.get_secret_value())



class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, storage: MemoryStorage) -> None:
        BaseMiddleware.__init__(self)
        self.storage = storage
    async def __call__(
            self,
            handler: Callable[[Message|None, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        user = f'user{event.from_user.id}'
        check_user = await self.storage.get_data(key=user)
        data_for_set = {"time": time.time()}
        if check_user:
            if data_for_set["time"] - check_user["time"] < 1:
                await event.answer('Не так быстро!\n\nВас заглушили за флуд. Подождите 3 секунды, чтобы воспользоваться услугами бота')
                print(f'Разница: {data_for_set["time"] - check_user["time"]}')
                time.sleep(5)
            else:
                await handler(event, data)
        else: 
            await handler(event, data)
        
                   

        await self.storage.set_data(key=user, data=data_for_set)
        # print('Got it') 