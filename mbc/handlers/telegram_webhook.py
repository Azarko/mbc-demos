import aiogram
import aiogram.types
from aiohttp import web

from mbc import types


async def handler(request: types.Request):
    update = await request.json()
    update = aiogram.types.Update(**update)
    aiogram.Bot.set_current(request.app.bot.bot)
    await request.app.bot.dispatcher.process_update(update)
    return web.json_response({})
