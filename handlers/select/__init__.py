import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from heidi import delivery
from heidi.queries import find_groups, find_supergroups, find_subscribers

from init import dp
from util import InteractionError

from middleware import authorize

import text

from handlers.select.markup import GROUP, SUPERGROUP, DONE, render
from handlers.select.misc import where_subscribers, validate_and_decompose, \
    mark_as_selected, find_by_id


class SelectState(StatesGroup):

    Buttons = State()
    Message = State()


@dp.message_handler(commands='select', state='*')
@authorize('trainer', 'staff')
async def select(ctx, message: types.Message):
    limit = await delivery.get_queue_limit(ctx.user)
    if limit.value >= limit.daily:
        raise InteractionError(text.queue_limit_exceeded(limit))

    ctx.groups = await find_groups(ctx.user)
    if not ctx.groups:
        raise InteractionError(text.NO_OWNERSHIP)

    ctx.subscribers = await find_subscribers(ctx.groups)

    if not ctx.subscribers:
        raise InteractionError(text.NO_SUBSCRIBERS)

    ctx.supergroups = await find_supergroups(ctx.user, ctx.groups)
    ctx.groups, ctx.supergroups = where_subscribers(ctx)

    ctx.selected = set()
    ctx.selected_tab = GROUP
    ctx.select_message = await message.answer(text.SELECT_HEADER,
                                              reply_markup=render(ctx))
    await SelectState.Buttons.set()


@dp.callback_query_handler(state=SelectState.Buttons)
@authorize('trainer', 'staff')
async def select_buttons(ctx, query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    if ctx.select_message.message_id != query.message.message_id:
        await query.message.answer(text.SESSION_EXPIRED)
        return

    if query.data == DONE:
        if not ctx.selected:
            ctx.clear()
            await query.message.edit_text(text.NOTHING_SELECTED)
            await state.finish()
        else:

            await query.message.edit_text(text.closed_select(ctx.selected),
                                          parse_mode='markdown')
            await SelectState.Message.set()
    elif query.data in (GROUP, SUPERGROUP):
        ctx.selected_tab = query.data
        await query.message.edit_reply_markup(render(ctx))
    else:
        is_supergroup, id = validate_and_decompose(query.data)
        if id is None:
            raise InteractionError(text.NICE_TRY)

        match = find_by_id(id,
                           ctx.supergroups if is_supergroup else ctx.groups)

        # Inline queries can be forged
        if not match:
            raise InteractionError(text.NICE_TRY)

        mark_as_selected(ctx, match)
        await query.message.edit_reply_markup(render(ctx))


@dp.message_handler(state=SelectState.Message, commands='cancel')
@authorize('trainer', 'staff')
async def select_message_cancel(ctx, message: types.Message,
                                state: FSMContext):
    ctx.clear()
    await state.finish()

    await message.answer(text.DELIVERY_CANCELLED)


@dp.message_handler(state=SelectState.Message)
@authorize('trainer', 'staff')
async def select_message(ctx, message: types.Message, state: FSMContext):
    # TODO: Delivery service response evaluation instead of prechecking
    user, selected = ctx.user, list(ctx.selected)

    ctx.clear()
    await state.finish()

    limit = await delivery.get_queue_limit(user)
    # User might've been sending messages in between steps via other channels
    if limit.value >= limit.daily:
        await state.finish()
        raise InteractionError(text.queue_limit_exceeded(limit))

    history_key = await delivery.get_history_key(user)
    # We expect two couriers to process the message: VK, Telegram
    tracker = asyncio.create_task(
        delivery.track(history_key, touch_count=2, timeout=5))

    deliver_at, scheduled = await delivery.groups(history_key, user, selected,
                                                  message.text, 'telegram')
    await message.answer(text.DELIVERY_QUEUED)

    history = timeouted = False
    if scheduled:
        tracker.cancel()
    else:
        history, timeouted = await tracker

    recipients = history.recipients if history else None
    await message.answer(
        text.delivery_feedback(scheduled, deliver_at, not timeouted,
                               recipients))
