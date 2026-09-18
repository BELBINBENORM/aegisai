import asyncio,time
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.prompts import SYSTEM_PROMPT
from app.agents.verification import verify_answer
from app.mcp.client import MCPClient
from app.llm.client import LLMClient
from app.security.prompt_guard import check_prompt
from app.security.output_guard import validate_output
from app.database.models import Message,AgentRun
from app.config.settings import settings
from app.rag.citations import citations
from app.rag.reranking import rerank
from app.rag.compression import compress
from app.cache.cache import get_cached,set_cached
from app.cache.keys import response_key

class MainAgent:
    def __init__(self, llm=None, mcp=None): self.llm=llm or LLMClient(); self.mcp=mcp or MCPClient()
    def _needs_web(self,q): return any(x in q.lower() for x in ["latest","current","today","online","recent","news"])
    def _needs_docs(self,q): return True
    async def run(self,db:AsyncSession,user_id:int,session_id:int,query:str,request_id:str,emit=None,clarification_answer:str|None=None):
        check_prompt(query); started=time.perf_counter(); run=AgentRun(session_id=session_id,request_id=request_id,model=settings.model_name); db.add(run); await db.commit()
        async def event(name,data=None):
            if emit: await emit(name,data or {})
        try:
            await event("planning",{"needs_documents":self._needs_docs(query),"needs_web":self._needs_web(query)})
            hist=await self.mcp.call_tool("get_chat_history",{"db":db,"session_id":session_id,"limit":12})
            evidence=[]
            if self._needs_docs(query):
                evidence=await self.mcp.call_tool("hybrid_search",{"db":db,"session_id":session_id,"query":query,"limit":8})
                await event("retrieval",{"count":len(evidence)})
            web=[]
            if self._needs_web(query):
                result=await self.mcp.call_tool("search_web",{"query":query,"limit":5}); web=result.get("results",[]) if isinstance(result,dict) else []
                await event("tool_result",{"tool":"search_web","count":len(web)})
            ranked=rerank(query,[type("C",(),{"id":e["chunk_id"],"document_id":e["document_id"],"content":e["content"],"page":e.get("page"),"document":type("D",(),{"filename":e["filename"]})()})() for e in evidence],6)
            ranked=compress(ranked)
            prompt=self._build_prompt(query,hist,ranked,web,clarification_answer)
            await event("agent_started")
            answer=validate_output(await self.llm.generate(prompt,SYSTEM_PROMPT))
            check=verify_answer(answer,evidence)
            await event("verification",{"passed":check.passed,"issues":check.issues})
            if not check.passed and evidence:
                answer += "\n\nNote: verification found potential insufficiency in the generated response."
            db.add(Message(session_id=session_id,role="user",content=query)); db.add(Message(session_id=session_id,role="assistant",content=answer))
            run.status="completed"; run.steps=1; run.tool_calls_count=int(bool(evidence))+int(bool(web)); await db.commit()
            key=response_key(user_id,session_id,query,settings.model_name); await set_cached(key,{"answer":answer,"citations":citations(ranked)},settings.cache_ttl_seconds)
            return {"status":"completed","answer":answer,"citations":citations(ranked),"clarification":None}
        except Exception as exc:
            await db.rollback(); run.status="failed"; run.error=str(exc); await db.commit(); raise
    def _build_prompt(self,q,hist,evidence,web,clarification):
        context="\n".join(f'{m["role"]}: {m["content"]}' for m in hist)
        docs="\n\n".join(f'[DOC {i+1}] {c.document.filename} p.{c.page}\n{c.content}' for i,c in enumerate(evidence)) or "No document evidence."
        webtxt="\n".join(str(x) for x in web) or "No web evidence."
        return f"Conversation:\n{context}\n\nDocument evidence:\n{docs}\n\nWeb evidence:\n{webtxt}\n\nUser question: {q}\nClarification answer: {clarification or 'none'}\nAnswer directly and cite document evidence by filename/page when used."
