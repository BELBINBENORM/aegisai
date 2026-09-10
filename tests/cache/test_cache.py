from unittest.mock import AsyncMock, patch

import pytest

from app.cache.cache import get_cached, set_cached, delete_cached


@pytest.mark.asyncio
async def test_get_cached():
    client = AsyncMock()
    client.get.return_value = "value"

    with patch("app.cache.cache.get_redis", return_value=client):
        result = await get_cached("test")

    assert result == "value"


@pytest.mark.asyncio
async def test_set_cached():
    client = AsyncMock()

    with patch("app.cache.cache.get_redis", return_value=client):
        await set_cached("test", "value", expire=60)

    client.set.assert_awaited_once_with("test", "value", ex=60)


@pytest.mark.asyncio
async def test_delete_cached():
    client = AsyncMock()

    with patch("app.cache.cache.get_redis", return_value=client):
        await delete_cached("test")

    client.delete.assert_awaited_once_with("test")