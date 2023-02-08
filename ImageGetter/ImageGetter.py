from typing import List, Dict


class ImageGetter:
    async def get_card(self, promt: str) -> bytes:
        raise NotImplementedError()

    async def get_n_cards(self, promt: str, n: int) -> List[bytes]:
        cards = []
        for i in range(n):
            cards.append(await self.get_card(promt))
        return cards

    def __init__(self, height: int, width: int):
        self.height = height
        self.width = width
        pass

    @staticmethod
    def build(config: Dict):
        subclasses = {cls.__name__: cls for cls in ImageGetter.__subclasses__()}
        cls_name = config['image_getter_class']
        return subclasses[cls_name](**config[cls_name])
