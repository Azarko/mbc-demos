from aiohttp import web
from aiohttp import web_request

from mbc import config
from mbc import telegram_bot


class Application(web.Application):
    config: config.ApplicationConfig
    bot: telegram_bot.Bot


class Request(web_request.Request):
    app: Application
