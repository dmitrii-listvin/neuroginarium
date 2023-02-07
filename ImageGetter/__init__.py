from typing import Dict
from .ImageGetter import ImageGetter
from .RandomImageGetter import RandomImageGetter

def get_image_getter(config: Dict):
    subclasses = {cls.__name__: cls for cls in ImageGetter.__subclasses__()}
    cls_name = next(iter(config))
    return subclasses[cls_name](**config[cls_name])