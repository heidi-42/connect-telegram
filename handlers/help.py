from aiogram import types

from middleware import authorize

from init import dp

import text


@dp.message_handler(commands='help')
@authorize('*')
async def help(ctx, message: types.Message):
    role = ctx.user is not None and ctx.user.role
    await message.answer(text.help(role), parse_mode='markdown')
