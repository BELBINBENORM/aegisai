from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.api.auth import verify_api_key
from app.api.rate_limit import rate_limit
from app.agents.tool_runner import approval_manager_global, ToolRunner

router = APIRouter(prefix="/approvals", tags=["approvals"], dependencies=[Depends(verify_api_key), Depends(rate_limit)])
approval_manager = approval_manager_global
tool_runner = ToolRunner(approval_manager=approval_manager)

class ApprovalDecision(BaseModel):
    approved: bool

@router.get("/{approval_id}")
async def get_approval(approval_id: str):
    approval = await approval_manager.get(approval_id)
    if not approval:
        raise HTTPException(404, "Approval not found")
    return approval.__dict__

@router.post("/{approval_id}/decision")
async def decide_approval(approval_id: str, decision: ApprovalDecision):
    approval = await approval_manager.decide(approval_id, decision.approved)
    if not approval:
        raise HTTPException(404, "Approval not found")
    result = None
    if approval.approved:
        try:
            result = await tool_runner.resume_approved(approval_id)
        except ValueError as exc:
            return {**approval.__dict__, "status": "approved", "resume_error": str(exc)}
    return {**approval.__dict__, "status": "completed" if result else "rejected", "result": result}
