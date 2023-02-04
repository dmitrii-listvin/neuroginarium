class ImageGetter:
    async def get_card(self, promt: str) -> str:
        raise NotImplementedError()

    async def get_n_cards(self, promt: str, n: int) -> list[str]:
        cards = []
        for i in range(n):
            cards.append(await self.get_card(promt))
        return cards

    def __init__(self, height, width):
        self.height = height
        self.width = width
        pass
