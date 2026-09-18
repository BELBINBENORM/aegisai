from pathlib import Path
ALLOWED={".pdf":"application/pdf",".docx":"application/vnd.openxmlformats-officedocument.wordprocessingml.document",".txt":"text/plain"}
def validate_upload(filename: str, content_type: str | None, size: int, max_size: int):
    suffix=Path(filename).suffix.lower()
    if suffix not in ALLOWED: raise ValueError("Unsupported file type")
    if size>max_size: raise ValueError("File exceeds configured size limit")
    return suffix
