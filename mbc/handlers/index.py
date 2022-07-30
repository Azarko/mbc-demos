from aiohttp import web

from mbc import types


async def handler(request: types.Request):
    return web.Response(text='Hello, world')
