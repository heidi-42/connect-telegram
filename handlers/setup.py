from asyncio import sleep

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from heidi.access import stash_contact, commit_contact

from init import dp
from util import InteractionError

from middleware import authorize

import text


class SetupState(StatesGroup):

    Email = State()
    Confirmation = State()


@dp.message_handler(commands='start', state='*')
@authorize('*')
async def start(ctx, message: types.Message):
    if ctx.user is not None:
        raise InteractionError(text.ALREADY_ACQUAINTED)

    for line in text.ACQUAINTANCE:
        await message.answer(line)
        # Human-ish delay
        await sleep(.3)
    await SetupState.Email.set()


@dp.message_handler(state=SetupState.Email,
                    content_types=types.ContentTypes.TEXT)
@authorize('*')
async def email(ctx, message: types.Message):
    await stash_contact(message.text, 'telegram', str(ctx.peer_id))

    ctx.unconfirmed.email = message.text
    await SetupState.Confirmation.set()
    await message.reply(text.CONFIRMATION_CODE_SENT)


@dp.message_handler(state=SetupState.Confirmation, commands='reset')
@authorize('*')
async def confirmation_reset(_, message: types.Message, state: FSMContext):
    await message.answer(text.RESET)
    await state.finish()


@dp.message_handler(state=SetupState.Confirmation, commands='repeat')
@authorize('*')
async def confirmation_repeat(ctx, message: types.Message):
    await stash_contact(ctx.unconfirmed.email, 'telegram', str(ctx.peer_id))
    await message.answer(text.CONFIRMATION_CODE_SENT_AGAIN)


@dp.message_handler(state=SetupState.Confirmation,
                    content_types=types.ContentTypes.TEXT)
@authorize('*')
async def confirmation(_, message: types.Message, state: FSMContext):
    await commit_contact(message.text)
    await message.answer(text.CONFIRMATION_DONE)
    await state.finish()
