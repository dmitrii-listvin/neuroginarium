class ImageStorage:
    async def if_path_exists(self, path: str) -> bool:
        raise NotImplementedError()

    async def load_image(self, path: str) -> bytes:
        raise NotImplementedError()

    async def save_image(self, image: bytes) -> str:
        raise NotImplementedError()

    def __init__(self):
        pass
