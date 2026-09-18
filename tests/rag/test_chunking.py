import pytest
from app.rag.chunking import chunk_text

def test_chunking_progresses(): assert len(chunk_text("a"*2500,1000,100))==3
def test_invalid_overlap():
    with pytest.raises(ValueError): chunk_text("abc",10,10)
