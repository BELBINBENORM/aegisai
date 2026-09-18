from __future__ import annotations
import httpx
from typing import Any
from app.config.settings import settings
from app.mcp.server import server

class RemoteMCPError(RuntimeError): pass

class MCPClient:
    def __init__(self, url: str | None = None, api_key: str | None = None, timeout: float = 30.0):
        self.url = url.rstrip('/') if url else None
        self.api_key = api_key or settings.mcp_api_key
        self.timeout = timeout
        self.remote = None
        if not self.url and settings.web_search_url and settings.web_search_api_key:
            from app.mcp.client import RemoteMCPClient
            self.remote = RemoteMCPClient(settings.web_search_url, settings.web_search_api_key, timeout=settings.web_search_timeout_seconds)

    async def list_tools(self):
        if self.url:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                r = await client.get(f'{self.url}/mcp/tools', headers={'X-API-Key': settings.mcp_api_key})
                r.raise_for_status(); return r.json().get('tools', [])
        local = server.list_tools()
        remote = await self.remote.list_tools() if self.remote else []
        return local + remote

    async def call_tool(self, name: str, arguments: dict[str, Any]):
        if self.url:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                r = await client.post(f'{self.url}/mcp/tools/{name}', json={'arguments': arguments}, headers={'X-API-Key': self.api_key})
                r.raise_for_status(); return r.json().get('result')
        if self.remote and (name.startswith('tavily_') or name == 'search_web'):
            remote_name = name if name.startswith('tavily_') else 'tavily_search'
            remote_args = arguments if name.startswith('tavily_') else {'query': arguments['query'], 'max_results': arguments.get('limit', 5)}
            return await self.remote.call_tool(remote_name, remote_args)
        return await server.call(name, arguments)

class RemoteMCPClient:
    def __init__(self, url, api_key=None, timeout=30.0):
        self.url, self.api_key, self.timeout = url, api_key, timeout
        self._session_id = None; self._initialized = False
    def _headers(self):
        h={'Accept':'application/json, text/event-stream','Content-Type':'application/json'}
        if self.api_key: h['Authorization']=f'Bearer {self.api_key}'
        if self._session_id: h['Mcp-Session-Id']=self._session_id
        return h
    async def _post(self,payload):
        async with httpx.AsyncClient(timeout=self.timeout) as c:
            r=await c.post(self.url,headers=self._headers(),json=payload); r.raise_for_status()
            self._session_id=r.headers.get('Mcp-Session-Id',self._session_id)
            if 'text/event-stream' in r.headers.get('content-type',''): return r.text
            return r.json() if r.content else None
    async def initialize(self):
        if self._initialized:return
        await self._post({'jsonrpc':'2.0','id':'1','method':'initialize','params':{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'AegisAI','version':'1.0.0'}}})
        await self._post({'jsonrpc':'2.0','method':'notifications/initialized','params':{}}); self._initialized=True
    async def list_tools(self):
        await self.initialize(); result=await self._post({'jsonrpc':'2.0','id':'2','method':'tools/list','params':{}})
        return result.get('result',{}).get('tools',[]) if isinstance(result,dict) else []
    async def call_tool(self,name,arguments):
        await self.initialize(); result=await self._post({'jsonrpc':'2.0','id':'3','method':'tools/call','params':{'name':name,'arguments':arguments}})
        return result.get('result') if isinstance(result,dict) else result
