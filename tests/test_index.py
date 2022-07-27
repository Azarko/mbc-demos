async def test_hello(web_app_client):
    response = await web_app_client.get("/")
    assert response.status == 200
    text = await response.text()
    assert "Hello, world" in text
