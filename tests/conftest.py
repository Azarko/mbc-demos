import pytest

from mbc.main import create_app


@pytest.fixture(name='web_app_client')
async def web_app_client(aiohttp_client):
    client = await aiohttp_client(create_app())
    yield client
