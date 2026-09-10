from app.agents.approval import ApprovalManager


def test_action_requires_approval():
    manager = ApprovalManager()

    approval = manager.request("delete document")

    assert manager.can_execute(approval) is False


def test_approved_action_can_execute():
    manager = ApprovalManager()

    approval = manager.request("delete document")
    manager.approve(approval)

    assert manager.can_execute(approval) is True


def test_rejected_action_cannot_execute():
    manager = ApprovalManager()

    approval = manager.request("delete document")
    manager.reject(approval)

    assert manager.can_execute(approval) is False