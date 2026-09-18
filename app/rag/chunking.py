from dataclasses import dataclass
@dataclass(frozen=True)
class ChunkData:
    index:int; text:str; page:int|None=None; section:str|None=None

def chunk_text(text:str, size:int=1000, overlap:int=150, page:int|None=None, section:str|None=None)->list[ChunkData]:
    if size<=0 or overlap<0 or overlap>=size: raise ValueError("overlap must be >= 0 and smaller than chunk size")
    text=" ".join(text.split())
    if not text: return []
    out=[]; start=0; i=0; step=size-overlap
    while start<len(text):
        out.append(ChunkData(i,text[start:start+size],page,section)); i+=1; start+=step
    return out
