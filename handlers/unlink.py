from dotmap import DotMap

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from heidi import queries

from init import dp
from middleware import authorize

import text


class UnlinkState(StatesGroup):

    Confirmation = State()


@dp.message_handler(state='*', commands='unlink')
@authorize('trainer', 'staff', 'student')
async def unlink(_, message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(text.YAY, text.NAY)
    await message.answer(text.UNLINK_WARNING, reply_markup=keyboard)
    await UnlinkState.Confirmation.set()


@dp.message_handler(state=UnlinkState.Confirmation,
                    content_types=types.ContentTypes.TEXT)
@authorize('trainer', 'staff', 'student')
async def unlink_confirmation(ctx, message: types.Message, state: FSMContext):
    if message.text == text.YAY:
        await queries.unlink(ctx.user.id, str(ctx.peer_id), 'telegram')
        ctx.clear()

        response = text.UNLINK_FINISH
    else:
        response = text.UNLINK_CANCELLED
    await state.finish()
    await message.answer(response, reply_markup=types.ReplyKeyboardRemove())
