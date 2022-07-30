import logging

from aiohttp import web

from mbc import config as config_module
from mbc import routes
from mbc import telegram_bot
from mbc import types


logger = logging.getLogger(__name__)


async def create_app(
        config: config_module.ApplicationConfig,
) -> types.Application:
    logging.basicConfig(level=logging.INFO)
    app = types.Application()
    app.config = config
    app.bot = telegram_bot.Bot(
        token=app.config.telegram_token,
        webhook_url=app.config.telegram_webhook_url,
    )

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    routes.setup_routes(app)
    return app


async def on_startup(app: types.Application):
    await app.bot.on_startup()


async def on_shutdown(app: types.Application):
    await app.bot.on_shutdown()


def main():
    config = config_module.ApplicationConfig.from_env()
    web.run_app(create_app(config=config), port=config.port)


if __name__ == '__main__':
    main()
