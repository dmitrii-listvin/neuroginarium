from typing import Dict


class ImageStorage:
    async def if_path_exists(self, path: str) -> bool:
        raise NotImplementedError()

    async def load_image(self, path: str) -> bytes:
        raise NotImplementedError()

    async def save_image(self, image: bytes) -> str:
        raise NotImplementedError()

    def __init__(self):
        pass

    @staticmethod
    def build(config: Dict):
        subclasses = {cls.__name__: cls for cls in ImageStorage.__subclasses__()}
        cls_name = config['image_storage_class']
        return subclasses[cls_name](**config[cls_name])
