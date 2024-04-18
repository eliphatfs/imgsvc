from typing_extensions import Literal


class ProcessRequest(object):
    def __init__(self, engine: Literal['cv2', 'pil'], src_url: str, dst_fmt: str) -> None:
        """
        `engine` is `cv2` or `pil`.
        `src_url` is an HTTP URL for the image to be processed.
        `dst_fmt` is the output format like `png` and `exr`.
        """
        super().__init__()
        self.engine = engine
        self.src = src_url
        self.enc = dst_fmt
        self.ops = []

    def crop(self, x: int, y: int, w: int, h: int) -> 'ProcessRequest':
        self.ops.append(["C", x, y, w, h])
        return self

    def resize(self, w: int, h: int, mode: int) -> 'ProcessRequest':
        self.ops.append(["R", w, h, mode])
        return self
