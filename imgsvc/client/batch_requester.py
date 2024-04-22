import io
import time
import tarfile
import requests
import requests.adapters
from typing import List
from .process_request import ProcessRequest


class BatchRequester(object):
    def __init__(self, endpoint) -> None:
        self.endpoint = endpoint

    def get(self, reqs: List[ProcessRequest], timeout=10, retries=2) -> List[bytes]:
        ser = [[req.engine, req.src, req.enc, req.ops] for req in reqs]
        session = requests.Session()
        session.mount('https://', requests.adapters.HTTPAdapter(pool_connections=0, pool_maxsize=0))
        for i in range(retries):
            try:
                post = requests.post(self.endpoint, json=ser, timeout=timeout)
            except requests.ConnectionError:
                if i == retries - 1:
                    raise
                time.sleep(i + 1)
                continue
            if post.status_code != 200:
                raise ValueError('request failed', post.text)
            recv = io.BytesIO(post.content)
            results = []
            with tarfile.TarFile(fileobj=recv) as tar:
                for i in range(len(reqs)):
                    results.append(tar.extractfile(str(i)).read())
            return results
