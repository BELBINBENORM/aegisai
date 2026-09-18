from app.security.pii import redact_pii


def test_redacts_email():
    result = redact_pii(
        "Contact user@example.com for details."
    )

    assert result == (
        "Contact [REDACTED_EMAIL] for details."
    )


def test_redacts_indian_phone_number():
    result = redact_pii(
        "Call +91 9876543210."
    )

    assert result == "Call [REDACTED_PHONE]."


def test_keeps_normal_text():
    text = "Python is useful for AI."

    assert redact_pii(text) == text