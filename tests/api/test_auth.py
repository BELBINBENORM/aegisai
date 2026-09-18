import pytest
from app.api.auth import verify_api_key
@pytest.mark.asyncio
async def test_auth_rejects_missing():
    with pytest.raises(Exception): await verify_api_key(None)
