from app.agents.evidence import verify_evidence
from app.security.output_guard import validate_output


def verify_answer(answer: str) -> bool:
    try:
        validate_output(answer)
    except ValueError:
        return False

    return verify_evidence(answer)