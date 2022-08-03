import http
import typing

import aiogram.utils.exceptions
import pytest

from mbc import telegram_bot

CHAT_ID = 123456789


@pytest.fixture(name='patch_send_message')
def _send_message(patch_method):
    """Patch aiogram.Bot.send_message and check message text (if specified)."""

    def decorator(expected_answer: typing.Optional[str]):
        @patch_method('aiogram.Bot.send_message')
        async def send_message(*args, chat_id, text, **kwargs):
            assert chat_id == CHAT_ID
            if expected_answer is not None:
                assert text == expected_answer

        return send_message

    return decorator


@pytest.fixture(name='patch_send_action')
def _patch_send_action(patch_method):
    """Patch aiogram.Bot.send_chat_action and check action name."""

    def decorator(action_name: str = aiogram.types.ChatActions.UPLOAD_VIDEO):
        @patch_method('aiogram.Bot.send_chat_action')
        async def send_chat_action(*args, chat_id, action):
            assert chat_id == CHAT_ID
            assert action == action_name

        return send_chat_action

    return decorator


def _create_request(text: str, chat_type: str = 'private') -> typing.Dict:
    return {
        'update_id': 147272840,
        'message': {
            'message_id': 561,
            'from': {
                'id': CHAT_ID,
                'is_bot': False,
                'first_name': 'Ivan',
                'last_name': 'Ivanov',
                'username': 'Ivan007',
                'language_code': 'ru',
            },
            'chat': {
                'id': CHAT_ID,
                'first_name': 'Ivan',
                'last_name': 'Ivanov',
                'username': 'Ivan007',
                'type': chat_type,
            },
            'date': 1659138663,
            'text': text,
            'entities': [
                {
                    'type': 'bot_command',
                    'offset': 0,
                    'length': 6,
                },
            ],
        },
    }


async def test_telegram_start(web_app_client, patch_send_message):
    patch_send_message('started')
    response = await web_app_client.post(
        '/api/v1/telegram/webhook',
        json=_create_request('/start'),
    )
    assert response.status == http.HTTPStatus.OK


async def test_telegram_bot_api_exception(web_app_client, patch_method):
    @patch_method('aiogram.Bot.send_message')
    async def send_message(*args, chat_id, text, **kwargs):
        assert chat_id == CHAT_ID
        assert text == 'started'
        raise aiogram.utils.exceptions.BotBlocked(
            'Forbidden: bot was blocked by the user',
        )

    response = await web_app_client.post(
        '/api/v1/telegram/webhook',
        json=_create_request('/start'),
    )
    assert response.status == http.HTTPStatus.OK


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

    @patch_method('mbc.telegram_bot._load_result')
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
        json=_create_request(f'/video_text {command_arg}'),
    )
    assert response.status == http.HTTPStatus.OK
    assert is_video_send == is_send


async def test_telegram_video_text_group(web_app_client, patch_send_message):
    patch_send_message('this function available only in private chat')
    response = await web_app_client.post(
        '/api/v1/telegram/webhook',
        json=_create_request('/video_text test', chat_type='group'),
    )
    assert response.status == http.HTTPStatus.OK


async def test_telegram_video_text_imaginator(
    web_app_client,
    patch_method,
    patch_send_action,
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
        json=_create_request('/video_text test'),
    )
    assert response.status == http.HTTPStatus.OK
    assert is_video_send
