from dataclasses import dataclass


@dataclass
class ApprovalRequest:
    action: str
    approved: bool = False


class ApprovalManager:
    def __init__(self):
        self.pending: list[ApprovalRequest] = []

    def request(self, action: str) -> ApprovalRequest:
        approval = ApprovalRequest(action=action)
        self.pending.append(approval)
        return approval

    def approve(self, approval: ApprovalRequest) -> None:
        approval.approved = True

    def reject(self, approval: ApprovalRequest) -> None:
        approval.approved = False

    def can_execute(self, approval: ApprovalRequest) -> bool:
        return approval.approved