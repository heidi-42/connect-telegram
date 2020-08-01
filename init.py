import sys
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from keyring import get_password

from heidi.util import init_data_layer


async def on_startup(*args, **kwargs):
    await init_data_layer({})


async def on_shutdown(dp: Dispatcher):
    await dp.storage.close()
    await dp.storage.wait_closed()


bot = Bot(get_password('telegram', 'heidi'))
storage = RedisStorage(password=get_password('redis', 'heidi'))
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
dp.middleware.setup(LoggingMiddleware())
