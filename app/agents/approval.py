from dataclasses import dataclass
from uuid import uuid4
import json
from app.cache.redis import get_redis

@dataclass
class ApprovalRequest:
    id: str
    action: str
    approved: bool = False
    rejected: bool = False

class ApprovalManager:
    PREFIX = "aegisai:approval:"
    def __init__(self):
        self.pending: dict[str, ApprovalRequest] = {}

    def request(self, action: str) -> ApprovalRequest:
        approval = ApprovalRequest(id=str(uuid4()), action=action)
        self.pending[approval.id] = approval
        return approval

    def approve(self, approval: ApprovalRequest) -> None:
        approval.approved = True; approval.rejected = False

    def reject(self, approval: ApprovalRequest) -> None:
        approval.approved = False; approval.rejected = True

    def can_execute(self, approval: ApprovalRequest) -> bool:
        return approval.approved and not approval.rejected

    async def persist(self, approval: ApprovalRequest) -> None:
        redis = await get_redis()
        if redis:
            await redis.set(self.PREFIX + approval.id, json.dumps(approval.__dict__), ex=86400)

    async def get(self, approval_id: str) -> ApprovalRequest | None:
        approval = self.pending.get(approval_id)
        if approval: return approval
        redis = await get_redis()
        if not redis: return None
        raw = await redis.get(self.PREFIX + approval_id)
        if not raw: return None
        data = json.loads(raw)
        approval = ApprovalRequest(**data)
        self.pending[approval.id] = approval
        return approval

    async def decide(self, approval_id: str, approved: bool) -> ApprovalRequest | None:
        approval = await self.get(approval_id)
        if not approval: return None
        if approved: self.approve(approval)
        else: self.reject(approval)
        await self.persist(approval)
        return approval
