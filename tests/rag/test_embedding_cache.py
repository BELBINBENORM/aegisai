from unittest.mock import AsyncMock, patch

import pytest

from app.rag.embedding_cache import get_embedding


@pytest.mark.asyncio
async def test_embedding_uses_redis_cache():
    cached_embedding = "[0.1, 0.2, 0.3]"

    with patch(
        "app.rag.embedding_cache.get_cached",
        new=AsyncMock(return_value=cached_embedding),
    ) as get_cached_mock, patch(
        "app.rag.embedding_cache.generate_embedding",
        new=AsyncMock(),
    ) as generate_mock:

        result = await get_embedding("hello")

    assert result == [0.1, 0.2, 0.3]
    get_cached_mock.assert_awaited_once()
    generate_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_embedding_generates_and_caches():
    embedding = [0.1, 0.2, 0.3]

    with patch(
        "app.rag.embedding_cache.get_cached",
        new=AsyncMock(return_value=None),
    ), patch(
        "app.rag.embedding_cache.generate_embedding",
        new=AsyncMock(return_value=embedding),
    ) as generate_mock, patch(
        "app.rag.embedding_cache.set_cached",
        new=AsyncMock(),
    ) as set_cached_mock:

        result = await get_embedding("hello")

    assert result == embedding
    generate_mock.assert_awaited_once_with("hello")
    set_cached_mock.assert_awaited_once()