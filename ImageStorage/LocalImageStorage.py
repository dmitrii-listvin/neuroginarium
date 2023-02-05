import os
import uuid
from pathlib import Path
from ImageStorage.ImageStorage import ImageStorage


class LocalImageStorage(ImageStorage):
    async def if_path_exists(self, path: str) -> bool:
        return os.path.exists(path)

    async def load_image(self, path: str) -> bytes:
        with open(path, "rb") as fb:
            res = fb.read()
        return res

    async def save_image(self, image: bytes) -> str:
        write_folder = f"{self.base_path}"
        Path(write_folder).mkdir(parents=True, exist_ok=True)
        filename = f"{uuid.uuid4()}.png"
        full_path = f"{write_folder}/{filename}"
        with open(full_path, "wb") as f:
            f.write(image)
        return full_path

    def __init__(self, base_path: str):
        super().__init__()
        self.base_path = base_path
