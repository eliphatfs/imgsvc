import io
from PIL import Image

from .abstract_engine import AbstractEngine


class PILEngine(AbstractEngine):
    def load(self, bs: bytes):
        return Image.open(bs)

    def crop(self, image: Image.Image, x: int, y: int, w: int, h: int):
        return image.crop((x, y, x + w, y + h))
    
    def resize(self, image: Image.Image, w: int, h: int, mode: int):
        return image.resize((w, h), resample=mode)

    def save(self, image: Image.Image, fmt: str) -> bytes:
        bs = io.BytesIO()
        if fmt == 'png':
            image.save(bs, fmt, compress_level=1)
        else:
            image.save(bs, fmt)
        return bs.getvalue()
