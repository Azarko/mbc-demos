import logging

import aiogram
import aiogram.types
from aiogram.utils import exceptions as aiogram_exceptions
from aiohttp import web

from mbc import types


logger = logging.getLogger(__name__)


async def handler(request: types.Request):
    update = await request.json()
    update = aiogram.types.Update(**update)
    logger.info(f'fetched webhook: {update}')
    aiogram.Bot.set_current(request.app.bot.bot)
    try:
        await request.app.bot.dispatcher.process_update(update)
    except aiogram_exceptions.BotBlocked as err:
        logger.warning(
            'fetched command from user which blocked bot', exc_info=err,
        )
    return web.json_response({})
