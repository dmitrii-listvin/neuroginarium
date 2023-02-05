import os
from ImageStorage.ImageStorage import ImageStorage


class LocalImageStorage(ImageStorage):
    async def if_path_exists(self, path: str) -> bool:
        return os.path.exists(path)

    async def load_image(self, path: str) -> bytes:
        with open(f"{self.base_path}/{path}", "rb") as fb:
            res = fb.read()
        return res

    async def save_image(self, image: bytes, path: str) -> bool:
        with open(f"{self.base_path}/{path}", 'wb') as f:
            f.write(image)
        return True

    def __init__(self, base_path: str):
        super().__init__()
        self.base_path = base_path
