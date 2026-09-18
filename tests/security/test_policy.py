from app.security.policy import requires_approval


def test_sensitive_action_requires_approval():
    assert requires_approval("delete_document") is True


def test_normal_action_does_not_require_approval():
    assert requires_approval("search_documents") is False


def test_unknown_action_does_not_require_approval():
    assert requires_approval("unknown_action") is False