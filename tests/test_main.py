import pytest
import asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app

@pytest.mark.asyncio
async def test_main():
    """Асинхронный тест главной ручки"""
    async with (AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    )) as client:
        res = await client.get("/")
        assert res.status_code == 200
        assert res.json() == {"message": "ok"}
