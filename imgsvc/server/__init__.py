import io
import os
import json
import tarfile
import argparse
import requests
import traceback
from urllib.parse import urlparse
from typing import List, Dict, Type
from multiprocessing.pool import ThreadPool, AsyncResult
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from ..engines import AbstractEngine, CV2Engine, PILEngine


def download_to_memory(req):
    try:
        idx, (engine, src, enc, ops) = req
        return idx, (engine, src, enc, ops), requests.get(src).content, None
    except Exception as exc:
        return None, None, None, exc


def execute_op(engine: AbstractEngine, x, op: list):
    opcode = op[0]
    if opcode == 'C':
        return engine.crop(x, *op[1:])
    elif opcode == 'R':
        return engine.resize(x, *op[1:])
    else:
        assert False, "unknown opcode %s" % opcode


def process_request(engine, enc, ops: List[list], x: bytes):
    try:
        instance = ImageServer.engines[engine]()
        x = instance.load(x)
        for op in ops:
            x = execute_op(instance, x, op)
        return instance.save(x, enc), None
    except Exception as exc:
        return None, exc


class ImageServer(BaseHTTPRequestHandler):
    engines: Dict[str, Type[AbstractEngine]] = {"cv2": CV2Engine, "pil": PILEngine}

    def error_response(self, code: int, message: str):
        self.send_response(code)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode())

    def do_POST(self):
        try:
            if 'Content-Length' not in self.headers:
                return self.error_response(411, "POST body should have Content-Length")
            content_len = int(self.headers['Content-Length'])
            post_body = self.rfile.read(content_len)
            try:
                reqs = json.loads(post_body)
            except json.JSONDecodeError as exc:
                return self.error_response(400, "Invalid POST JSON: %s" % str(exc))
            if not isinstance(reqs, list):
                return self.error_response(400, "Invalid request: not an array")
            if len(reqs) > 128:
                return self.error_response(400, "Invalid request: only max 128 images per request")
            tasks: Dict[int, AsyncResult] = {}

            if len(allow_url_hosts):
                for req in reqs:
                    engine, src, enc, ops = req
                    host = urlparse(src).hostname
                    if host not in allow_url_hosts:
                        return self.error_response(403, "Disallowed hostname for download: %s" % host)

            for idx, req, bts, err in io_pool.imap_unordered(download_to_memory, enumerate(reqs)):
                engine, src, enc, ops = req
                if err is not None:
                    return self.error_response(410, "Download request failed for %s: %s" % (src, repr(err)))
                tasks[idx] = engine_pool.apply_async(process_request, (engine, enc, ops, bts))
            fh = io.BytesIO()
            with tarfile.TarFile(fileobj=fh, mode="w") as tar:
                for idx in range(len(reqs)):
                    info = tarfile.TarInfo("%d" % idx)
                    data, err = tasks[idx].get()
                    if err is not None:
                        return self.error_response(415, "Fail to process image %s: %s" % (reqs[idx][1], repr(err)))
                    info.size = len(data)
                    tar.addfile(info, io.BytesIO(data))
            self.send_response(200)
            self.send_header('Content-Type', 'application/x-tar')
            self.end_headers()
            self.wfile.write(fh.getvalue())
        except Exception as exc:
            return self.error_response(500, traceback.format_exc())


def main():
    global engine_pool, io_pool, allow_url_hosts
    argp = argparse.ArgumentParser()
    argp.add_argument("--io-threads", default=int(os.getenv("IMGSVC_IO_THREADS", 32)), type=int)
    argp.add_argument("--engine-threads", default=int(os.getenv("IMGSVC_ENGINE_THREADS", 8)), type=int)
    argp.add_argument("--allow-url-hosts", default=os.getenv("IMGSVC_ALLOW_URL_HOSTS", "").split(), nargs='*')
    args = argp.parse_args()
    allow_url_hosts = set(args.allow_url_hosts)
    with ThreadPool(args.io_threads) as io_pool, ThreadPool(args.engine_threads) as engine_pool:
        with ThreadingHTTPServer(('127.0.0.1', 80), ImageServer) as server:
            print("Serving at http://127.0.0.1:80")
            server.serve_forever()
