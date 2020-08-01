from base64 import b64encode, b64decode

import pickle

from dotmap import DotMap

from aiogram import types

from init import dp


class InteractionError(Exception):
    pass


# TODO: Custom aiogram redis-based dispatcher storage


async def copy_context() -> DotMap:
    peer = types.User.get_current()
    state = dp.current_state(user=peer.id)

    data = await state.get_data()
    # `aiogram.contrib.dispatcher.storage.RedisStorage` utilizes `json.dumps`,
    # `json.loads` for the serialization matters and both of them, being
    # executed on a `str` input, return it unprocessed.
    if type(data) is str:
        data = pickle.loads(b64decode(data))
    return DotMap(data, peer_id=peer.id)


async def update_context(new_value: DotMap):
    peer = types.User.get_current()
    state = dp.current_state(user=peer.id)
    # base64 only uses ASCII characters
    await state.set_data(b64encode(pickle.dumps(new_value)).decode('ascii'))
