import typing

import aiogram
import pytest


CHAT_ID = 123456789


@pytest.fixture
def telegram_request():
    def decorator(
        text: str,
        chat_type: str = 'private',
        chat_id: int = CHAT_ID,
    ):
        return {
            'update_id': 147272840,
            'message': {
                'message_id': 561,
                'from': {
                    'id': chat_id,
                    'is_bot': False,
                    'first_name': 'Ivan',
                    'last_name': 'Ivanov',
                    'username': 'Ivan007',
                    'language_code': 'ru',
                },
                'chat': {
                    'id': chat_id,
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

    return decorator


# TODO: save call info (times called, sent text, etc)
@pytest.fixture
def patch_send_message(patch_method):
    """Patch aiogram.Bot.send_message and check message text (if specified)."""

    def decorator(
        expected_answer: typing.Optional[str],
        expected_chat_id: int = CHAT_ID,
    ):
        @patch_method('aiogram.Bot.send_message')
        async def send_message(*args, chat_id, text, **kwargs):
            assert chat_id == expected_chat_id
            if expected_answer is not None:
                assert text == expected_answer

        return send_message

    return decorator


@pytest.fixture
def patch_send_action(patch_method):
    """Patch aiogram.Bot.send_chat_action and check action name."""

    def decorator(action_name: str = aiogram.types.ChatActions.UPLOAD_VIDEO):
        @patch_method('aiogram.Bot.send_chat_action')
        async def send_chat_action(*args, chat_id, action):
            assert chat_id == CHAT_ID
            assert action == action_name

        return send_chat_action

    return decorator
