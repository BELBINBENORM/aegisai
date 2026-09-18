import json
from app.cache.redis import get_redis
QUEUE="aegisai:jobs"
async def enqueue_job(job_id,job_type,payload):
    r=await get_redis()
    if not r: return False
    await r.rpush(QUEUE,json.dumps({"job_id":job_id,"type":job_type,"payload":payload})); return True
async def get_queued():
    r=await get_redis()
    if not r:return None
    item=await r.lpop(QUEUE); return json.loads(item) if item else None


class JobManager:
    def __init__(self):
        self._tasks = {}
    async def submit(self, job_id, func):
        import asyncio
        self._tasks[job_id] = asyncio.create_task(self._run(job_id, func))
    async def _run(self, job_id, func):
        try: await func()
        finally: self._tasks.pop(job_id, None)
    async def is_running(self, job_id):
        task=self._tasks.get(job_id); return bool(task and not task.done())
