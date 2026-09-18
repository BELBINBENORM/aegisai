from sqlalchemy.ext.asyncio import AsyncSession
from app.rag.retrieval import Retriever
async def hybrid_search(db:AsyncSession,session_id:int,query:str,limit:int=6):
    chunks=await Retriever().hybrid_search(db,session_id,query,limit)
    return [{"chunk_id":c.id,"document_id":c.document_id,"filename":c.document.filename,"page":c.page,"content":c.content} for c in chunks]
