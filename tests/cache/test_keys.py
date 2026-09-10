from app.cache.keys import build_response_cache_key


def test_response_cache_key_is_stable():
    key1 = build_response_cache_key("hello", "user-1")
    key2 = build_response_cache_key("hello", "user-1")

    assert key1 == key2


def test_response_cache_key_is_user_specific():
    key1 = build_response_cache_key("hello", "user-1")
    key2 = build_response_cache_key("hello", "user-2")

    assert key1 != key2


def test_response_cache_key_does_not_contain_query():
    key = build_response_cache_key("my secret question", "user-1")

    assert "my secret question" not in key