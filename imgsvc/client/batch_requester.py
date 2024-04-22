import io
import tarfile
import requests
from typing import List
from .process_request import ProcessRequest


class BatchRequester(object):
    def __init__(self, endpoint) -> None:
        self.endpoint = endpoint

    def get(self, reqs: List[ProcessRequest], timeout=10, retries=2) -> List[bytes]:
        ser = [[req.engine, req.src, req.enc, req.ops] for req in reqs]
        for i in range(retries):
            try:
                post = requests.post(self.endpoint, json=ser, timeout=timeout)
            except requests.ConnectionError:
                if i == retries - 1:
                    raise
                continue
            if post.status_code != 200:
                raise ValueError('request failed', post.text)
            recv = io.BytesIO(post.content)
            results = []
            with tarfile.TarFile(fileobj=recv) as tar:
                for i in range(len(reqs)):
                    results.append(tar.extractfile(str(i)).read())
            return results
