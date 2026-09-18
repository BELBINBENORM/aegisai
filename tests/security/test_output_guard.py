import pytest

from app.security.output_guard import validate_output


def test_valid_output():
    assert validate_output("  Hello world  ") == "Hello world"


def test_rejects_empty_output():
    with pytest.raises(ValueError, match="Invalid empty output"):
        validate_output("")


def test_rejects_whitespace_output():
    with pytest.raises(ValueError, match="Invalid empty output"):
        validate_output("   ")