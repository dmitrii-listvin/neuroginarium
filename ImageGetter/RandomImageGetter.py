from ImageGetter.ImageGetter import ImageGetter
import uuid
from randimage import get_random_image
from matplotlib.image import imsave


class RandomImageGetter(ImageGetter):
    def __init__(self, height, width):
        super().__init__(height, width)

    async def get_card(self, promt: str) -> str:
        img_size = (self.height, self.width)
        img = get_random_image(img_size)  # returns numpy array

        filepath = (
            f"tmp/{str(uuid.uuid4())}.png"  # will need abstraction for filesystem / db
        )
        imsave(f"{filepath}", img)
        return filepath
