import base64
import requests
from image_getter.image_getter import ImageGetter
from typing import Optional


class UrlImageGetter(ImageGetter):
    def __init__(self, url):
        super().__init__()
        self.url = url

    async def get_card(self, promt: str) -> Optional[bytes]:

        json_data = {
            'prompt': promt,
        }

        response = requests.post(self.url, headers={}, json=json_data)

        if response.status_code == 200:
            image_str = response.json()["image"]
            return base64.b64decode(image_str.encode())
        else:
            return None
