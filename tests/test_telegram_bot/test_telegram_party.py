import http

import pytest


async def test_telegram_party(
    web_app_client,
    patch_send_message,
    telegram_request,
):
    patch_send_message(
        'input members and payments separated by space, one member per line, '
        'for example: \n\nperson_one 1000\nperson_two 2000',
    )
    response = await web_app_client.post(
        '/api/v1/telegram/webhook',
        json=telegram_request('/party'),
    )
    assert response.status == http.HTTPStatus.OK


@pytest.mark.parametrize(
    ('request_text', 'expected_answer'),
    (
        pytest.param(
            'person_one 1000',
            'each member must pay: 1000.00\n\nperson_one: 0.00',
            id='OK-one-row',
        ),
        pytest.param(
            'person_one 1000\nperson_two 500',
            'each member must pay: 750.00\n\nperson_one: -250.00\nperson_two:'
            ' 250.00',
            id='OK-two-rows',
        ),
        pytest.param(
            'person_one -1000\nperson_two +2000',
            'each member must pay: 500.00\n\nperson_one: 1500.00\n'
            'person_two: -1500.00',
            id='signs',
        ),
        pytest.param(
            'person_one 1000.50',
            'each member must pay: 1000.50\n\nperson_one: 0.00',
            id='decimal',
        ),
        pytest.param(
            'person_one 1000 ',
            'can\'t parse string 1 ("person_one 1000 "): invalid string'
            ' format',
            id='wrong-format-space-at-end',
        ),
        pytest.param(
            'person_one 1000 qwe',
            'can\'t parse string 1 ("person_one 1000 qwe"): invalid string'
            ' format',
            id='wrong-format-trash',
        ),
        pytest.param(
            'person_one 100000000000000000\nperson_two 5730000000000000000',
            'each member must pay: 2915000000000000000.00\n\n'
            'person_one: 2815000000000000000.00\nperson_two: '
            '-2815000000000000000.00',
            id='big-numbers',
        ),
        pytest.param(
            'person_one -100000\nperson_two +200',
            'each member must pay: -49900.00\n\nperson_one: 50100.00\n'
            'person_two: -50100.00',
            id='negative-avg',
        ),
    ),
)
async def test_telegram_party_calc(
    web_app_client,
    patch_send_message,
    telegram_request,
    request_text,
    expected_answer,
):
    web_app_client.app.bot.storage.data = {
        '123456789': {
            '123456789': {'state': 'Form:data', 'data': {}, 'bucket': {}},
        },
    }

    patch_send_message(str(expected_answer))
    response = await web_app_client.post(
        '/api/v1/telegram/webhook',
        json=telegram_request(request_text),
    )
    assert response.status == http.HTTPStatus.OK
    assert '123456789' not in web_app_client.app.bot.storage.data
