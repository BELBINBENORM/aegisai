from dataclasses import dataclass
@dataclass
class VerificationResult:
    passed:bool; issues:list[str]

def verify_answer(answer:str,evidence:list[dict]):
    issues=[]
    if not answer.strip(): issues.append("empty answer")
    if evidence and len(answer.strip())<20: issues.append("answer may be insufficient")
    return VerificationResult(not issues,issues)
