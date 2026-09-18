SENSITIVE_ACTIONS = {
    "delete_document",
    "delete_memory",
    "send_message",
    "modify_data",
}


def requires_approval(action: str) -> bool:
    return action in SENSITIVE_ACTIONS