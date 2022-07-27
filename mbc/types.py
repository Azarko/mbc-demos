from aiohttp import web
from aiohttp import web_request

from mbc import config


class Application(web.Application):
    config: config.ApplicationConfig


class Request(web_request.Request):
    app: Application
