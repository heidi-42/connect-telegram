import asyncio

from aiogram import types, executor

from heidi.util import init_data_layer

from init import dp, on_startup, on_shutdown
from middleware import fearward

import handlers.setup
import handlers.unlink
import handlers.select
import handlers.help

import text


@dp.message_handler()
async def fallback(message: types.Message):
    await message.answer(text.EPERM)


executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
