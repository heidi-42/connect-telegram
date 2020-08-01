from functools import wraps

from aiogram import types

from heidi.queries import find_user
from heidi.ex import ServerError, ConnectionError, HeidiError
from heidi.util import GinoException, RedisError

from init import bot
from util import copy_context, update_context, InteractionError

import text


def authorize(*compliant_roles):
    def decorator(handler):
        @wraps(handler)
        async def decorated(ctx, *args, **kwargs):
            user = await find_user(str(ctx.peer_id), 'telegram')

            if '*' not in compliant_roles:
                if user is None:
                    raise InteractionError(text.EPERM)

                if user.role not in compliant_roles:
                    raise InteractionError(text.EPERM)

            ctx.user = user
            return await handler(ctx, *args, **kwargs)

        # We don't use it singly anyway
        return fearward(with_context(decorated))

    return decorator


def fearward(handler):
    """`heidi.util.fearward` Telegram analogue. DIYing middlewares because
    `aiogram` middleware engine isn't documented at all as of 20/07/29.
    """
    @wraps(handler)
    async def decorated(*args, **kwargs):
        peer_id = (types.User.get_current()).id
        try:
            return await handler(*args, **kwargs)
        except (ServerError, ConnectionError, GinoException, RedisError):
            await bot.send_message(peer_id, text.SOMETHING_AWFUL)
        except HeidiError as e:
            error = str(e)
            if error in text.localized:
                error = text.localized[error]
            else:
                error = text.SOMETHING_AWFUL
            await bot.send_message(peer_id, error)
        except InteractionError as e:
            await bot.send_message(peer_id, str(e))
        except Exception:
            await bot.send_message(peer_id, text.CHOCO_AWAITS)

    return decorated


def with_context(handler):
    @wraps(handler)
    async def decorated(*args, **kwargs):
        ctx = await copy_context()
        await handler(ctx, *args, **kwargs)
        await update_context(ctx)

    return decorated
