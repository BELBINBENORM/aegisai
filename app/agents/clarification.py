from dataclasses import dataclass
@dataclass
class ClarificationRequest:
    message:str; options:list[dict]; allow_custom:bool=True

def build_clarification(message, options, allow_custom=True): return {"type":"clarification","message":message,"options":options,"allow_custom":allow_custom}
