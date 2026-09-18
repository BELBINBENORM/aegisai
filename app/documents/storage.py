from pathlib import Path
import shutil
from app.config.settings import settings
class LocalFileStorage:
    def __init__(self, root=None): self.root=Path(root or settings.object_storage_dir); self.root.mkdir(parents=True,exist_ok=True)
    async def save(self, key: str, fileobj):
        path=self.root/key; path.parent.mkdir(parents=True,exist_ok=True)
        with path.open("wb") as out: shutil.copyfileobj(fileobj,out)
        return str(path)
    def open(self,key): return open(self.root/key,"rb")
    async def delete(self,key):
        p=self.root/key
        if p.exists(): p.unlink()
