import cv2
import numpy

from .abstract_engine import AbstractEngine


class CV2Engine(AbstractEngine):
    def load(self, bs: bytes):
        dec = cv2.imdecode(numpy.frombuffer(bs, dtype=numpy.uint8), cv2.IMREAD_UNCHANGED)
        if dec is None:
            raise ValueError("cv2 cannot load image")
        return dec
    
    def crop(self, image, x: int, y: int, w: int, h: int):
        return image[y: y + h, x: x + w]

    def resize(self, image, w: int, h: int, mode: int):
        return cv2.resize(image, (w, h), interpolation=mode)

    def save(self, image, fmt: str) -> bytes:
        success, buf = cv2.imencode('.' + fmt, image)
        if not success:
            raise ValueError("cv2 cannot encode image")
        return buf.tobytes()
