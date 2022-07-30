import pytest

from mbc import config
from mbc.main import create_app


@pytest.fixture(name='web_app_client')
async def web_app_client(aiohttp_client):
    cfg = config.ApplicationConfig(
        port=3000,
        telegram_token='123:awesome-token',
        telegram_webhook_url='',
        is_test=True,
    )
    client = await aiohttp_client(await create_app(cfg))
    yield client


@pytest.fixture
def patch_method(monkeypatch):
    def decorator_factory(path):
        def decorator(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            monkeypatch.setattr(path, wrapper)
            return wrapper
        return decorator
    return decorator_factory
