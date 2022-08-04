import http


async def test_hello(web_app_client):
    response = await web_app_client.get('/')
    assert response.status == http.HTTPStatus.OK
    text = await response.text()
    assert 'Hello, world' in text
