import os

from aiohttp import web


PORT = os.environ.get('PORT', '8080')


def setup_routes(app):
    app.router.add_get('/', index)


async def index(request):
    return web.Response(text='hello world')


def create_app():
    app = web.Application()
    setup_routes(app)
    return app


def main():
    app = create_app()
    web.run_app(app, port=PORT)


if __name__ == '__main__':
    main()
