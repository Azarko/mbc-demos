import http

import aiogram.utils.exceptions


async def test_telegram_start(
    web_app_client,
    patch_send_message,
    telegram_request,
):
    patch_send_message('started')
    response = await web_app_client.post(
        '/api/v1/telegram/webhook',
        json=telegram_request('/start'),
    )
    assert response.status == http.HTTPStatus.OK


async def test_telegram_bot_api_exception(
    web_app_client,
    patch_method,
    telegram_request,
):
    @patch_method('aiogram.Bot.send_message')
    async def send_message(*args, text, **kwargs):
        assert text == 'started'
        raise aiogram.utils.exceptions.BotBlocked(
            'Forbidden: bot was blocked by the user',
        )

    response = await web_app_client.post(
        '/api/v1/telegram/webhook',
        json=telegram_request('/start'),
    )
    assert response.status == http.HTTPStatus.OK
