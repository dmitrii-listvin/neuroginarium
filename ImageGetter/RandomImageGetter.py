from io import BytesIO
from ImageGetter.ImageGetter import ImageGetter
from randimage import get_random_image
from matplotlib.image import imsave


class RandomImageGetter(ImageGetter):
    def __init__(self, height, width):
        super().__init__(height, width)

    async def get_card(self, promt: str) -> bytes:
        img_size = (self.height, self.width)
        img = get_random_image(img_size)  # returns numpy array

        buf = BytesIO()
        imsave(buf, img)
        buf.seek(0)

        return buf.read()
