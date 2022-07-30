from mbc import types
from mbc.handlers import index
from mbc.handlers import telegram_webhook


def setup_routes(app: types.Application):
    app.router.add_get('/', index.handler)
    app.router.add_post('/api/v1/telegram/webhook', telegram_webhook.handler)
