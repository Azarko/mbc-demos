import http


CHAT_ID = 123456789


async def test_telegram(web_app_client, patch_method):
    @patch_method('aiogram.Bot.send_message')
    async def send_message(*args, chat_id, text, **kwargs):
        assert chat_id == CHAT_ID
        assert text == 'started'

    request_data = {
        "update_id": 147272840,
        "message": {
            "message_id": 561,
            "from": {
                "id": CHAT_ID,
                "is_bot": False,
                "first_name": "Ivan",
                "last_name": "Ivanov",
                "username": "Ivan007",
                "language_code": "ru",
            },
            "chat": {
                "id": CHAT_ID,
                "first_name": "Ivan",
                "last_name": "Ivanov",
                "username": "Ivan007",
                "type": "private",
            },
            "date": 1659138663,
            "text": "/start",
            "entities": [
                {
                    "type": "bot_command",
                    "offset": 0,
                    "length": 6,
                },
            ],
        },
    }
    response = await web_app_client.post(
        "/api/v1/telegram/webhook", json=request_data,
    )
    assert response.status == http.HTTPStatus.OK
