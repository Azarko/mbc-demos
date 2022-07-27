from aiohttp import web

from mbc import types


async def index(request: types.Request):
    return web.Response(text='Hello, world')
