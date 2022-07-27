from aiohttp import web

from mbc import config as config_module
from mbc import routes
from mbc import types


def create_app() -> types.Application:
    app = types.Application()
    app.config = config_module.ApplicationConfig.from_env()
    routes.setup_routes(app)
    return app


def main():
    app = create_app()
    web.run_app(app, port=app.config.port)


if __name__ == '__main__':
    main()
