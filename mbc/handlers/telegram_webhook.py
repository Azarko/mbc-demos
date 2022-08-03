import logging

import aiogram
import aiogram.types
from aiohttp import web

from mbc import types


logger = logging.getLogger(__name__)


async def handler(request: types.Request):
    update = await request.json()
    update = aiogram.types.Update(**update)
    logger.info(f'fetched webhook: {update}')
    aiogram.Bot.set_current(request.app.bot.bot)
    await request.app.bot.dispatcher.process_update(update)
    return web.json_response({})
