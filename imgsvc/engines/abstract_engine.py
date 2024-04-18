class AbstractEngine:
    def load(self, bs: bytes):
        raise NotImplementedError

    def crop(self, image, x: int, y: int, w: int, h: int):
        raise NotImplementedError

    def resize(self, image, w: int, h: int, mode: int):
        raise NotImplementedError

    def save(self, image, fmt: str) -> bytes:
        raise NotImplementedError
