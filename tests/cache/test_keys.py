from app.cache.keys import response_key
def test_key_isolated(): assert response_key(1,2,"q","m")!=response_key(2,2,"q","m")
