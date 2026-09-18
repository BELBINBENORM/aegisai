from pathlib import Path
from pypdf import PdfReader
from docx import Document as DocxDocument

def load_file(path:str, suffix:str):
    if suffix==".txt": return [(None,Path(path).read_text(encoding="utf-8",errors="ignore"),None)]
    if suffix==".pdf":
        reader=PdfReader(path); return [(i+1,(p.extract_text() or ""),None) for i,p in enumerate(reader.pages)]
    if suffix==".docx":
        doc=DocxDocument(path); return [(None,"\n".join(p.text for p in doc.paragraphs),None)]
    raise ValueError("Unsupported file type")
