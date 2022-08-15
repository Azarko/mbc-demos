import http

import aiogram
import pytest

from mbc import telegram_bot


@pytest.mark.parametrize(
    ('command_arg', 'expected_answer', 'is_send'),
    (
        pytest.param('test', None, True, id='OK'),
        pytest.param(
            't' * (telegram_bot.MAX_TEXT_SIZE + 1),
            'Your message too long! Max message size is 150',
            False,
            id='too-long-message',
        ),
        pytest.param(
            '',
            'input text after command, please',
            False,
            id='no-command',
        ),
    ),
)
async def test_telegram_video_text(
    web_app_client,
    patch_method,
    patch_send_message,
    patch_send_action,
    telegram_request,
    command_arg,
    expected_answer,
    is_send,
):
    video_content = b'dummy-video-content'
    is_video_send = False
    patch_send_message(str(expected_answer))
    patch_send_action(aiogram.types.ChatActions.UPLOAD_VIDEO)

    @patch_method('imaginator.entry.create_video')
    def create_video(*args, text_line: str, **kwargs):
        assert text_line == command_arg

    @patch_method('mbc.utils.video_generator._load_result')
    def _load_result(*args, **kwargs):
        return video_content

    @patch_method('aiogram.Bot.send_animation')
    async def send_animation(*args, animation, **kwargs):
        content = animation.read()
        nonlocal is_video_send
        is_video_send = True
        assert content == video_content

    response = await web_app_client.post(
        '/api/v1/telegram/webhook',
        json=telegram_request(f'/video_text {command_arg}'),
    )
    assert response.status == http.HTTPStatus.OK
    assert is_video_send == is_send


async def test_telegram_video_text_group(
    web_app_client,
    patch_send_message,
    telegram_request,
):
    patch_send_message('this function available only in private chat')
    response = await web_app_client.post(
        '/api/v1/telegram/webhook',
        json=telegram_request('/video_text test', chat_type='group'),
    )
    assert response.status == http.HTTPStatus.OK


async def test_telegram_video_text_imaginator(
    web_app_client,
    patch_method,
    patch_send_action,
    telegram_request,
):
    is_video_send = False
    patch_send_action(aiogram.types.ChatActions.UPLOAD_VIDEO)

    @patch_method('aiogram.Bot.send_animation')
    async def send_animation(*args, animation, **kwargs):
        assert animation
        nonlocal is_video_send
        is_video_send = True

    response = await web_app_client.post(
        '/api/v1/telegram/webhook',
        json=telegram_request('/video_text test'),
    )
    assert response.status == http.HTTPStatus.OK
    assert is_video_send
