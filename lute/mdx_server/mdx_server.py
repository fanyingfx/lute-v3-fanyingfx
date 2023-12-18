# -*- coding: utf-8 -*-
# version: python 3.5

from socketserver import BaseServer
import threading
import re
import os
import sys

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import socketserver


from wsgiref.simple_server import make_server
from lute.mdx_server.mdx_util import *
from mdict_query.mdict_query import IndexBuilder
from urllib.parse import urlparse, parse_qs, unquote

"""
browser URL:
http://localhost:8000/test
"""

content_type_map = {
    "html": "text/html; charset=utf-8",
    "js": "application/x-javascript",
    "ico": "image/x-icon",
    "css": "text/css",
    "jpg": "image/jpeg",
    "png": "image/png",
    "bmp": "image/bmp",
    "gif": "image/gif",
    "mp3": "audio/mpeg",
    "mp4": "audio/mp4",
    "wav": "audio/wav",
    "ogg": "audio/ogg",
    "eot": "font/opentype",
    "svg": "text/xml",
    "ttf": "application/x-font-ttf",
    "woff": "application/x-font-woff",
    "woff2": "application/font-woff2",
}

from pathlib import Path

# resource_path = Path("D:/dicts/Eng/olad10/")
# from pathlib import Path
#
# resource_path = Path("D:/dicts/ja/Shogakukanjcv3")
# resource_path = os.path.join(base_path, 'mdx')
from typing import List


def get_local_resource(resource_paths: List[Path]):
    local_map = {}
    for resource_path in resource_paths:
        for item in resource_path.iterdir():
            if item.suffix[1:] in content_type_map:
                with open(item, "rb") as f:
                    content = f.read()
                    local_map[item.name] = content

    return local_map


# get_local_resource(resource_path)
# print(local_map.keys())


# print("resouce path : " + resource_path)
builder = None


class MDXDict:
    def __init__(self, builder: IndexBuilder, local_map=None, name=None) -> None:
        self.builder = builder
        if local_map is None:
            self.local_map = {}
        else:
            self.local_map = local_map
        self.name = name

    def lookup(self, resource_path):
        file_extension = resource_path.split(".")[-1]
        res = b""
        if resource_path.lstrip("/") in self.local_map:
            res = self.local_map[resource_path.lstrip("/")]
        elif file_extension in content_type_map:
            res = get_definition_mdd(resource_path, self.builder)
        else:
            res = get_definition_mdx(resource_path.lstrip("/"), self.builder)
        if res is None:
            res = b""
            print("none", resource_path)
        return res


class RequestHandler(BaseHTTPRequestHandler):
    def __init__(
        self,
        request,
        client_address,
        server,
        mdx_dict: IndexBuilder,
        local_map=dict(),
        mdx_dict2: IndexBuilder = None,
    ) -> None:
        self.mdx_dict = MDXDict(mdx_dict, local_map)
        if mdx_dict2 is not None:
            self.mdx_dict2 = MDXDict(mdx_dict2, local_map)
        else:
            self.mdx_dict2 = None
        # self.mdx_dict2=mdx_dict2
        super().__init__(request, client_address, server)

    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        return super().end_headers()

    def _set_response(self, status_code=200, headers=None):
        self.send_response(status_code)
        if headers:
            for header, value in headers.items():
                self.send_header(header, value)
        self.end_headers()

    def do_GET(self):
        parsed_url = urlparse(self.path)

        params = parse_qs(parsed_url.query)
        # print(parsed_url,params,file_util_get_ext(parsed_url.geturl()))
        parsed_url = unquote(parsed_url.geturl())

        # print(parsed_url)
        file_extension = parsed_url.split(".")[-1]
        # print('url',parsed_url,parsed_url[1:],parsed_url[1:] in local_map)
        # content_type =
        content_type = content_type_map.get(file_extension, "text/html; charset=utf-8")
        # res=

        res = self.mdx_dict.lookup(parsed_url)
        if res == b"" and self.mdx_dict2 is not None:
            res = self.mdx_dict2.lookup(parsed_url)
        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.end_headers()
        self.wfile.write(res)


def run_server(builder: IndexBuilder, local_map={}, port=8000, builder2=None):
    host = "lute.local"
    port = port

    server_address = (host, port)

    with socketserver.TCPServer(
        server_address,
        lambda request, client_address, server: RequestHandler(
            request, client_address, server, builder, local_map, builder2
        ),
    ) as httpd:
        print(f"Server running on {host}:{port}")
        httpd.serve_forever()

    # httpd = HTTPServer(server_address, RequestHandler)
    # with socketserver.TCPServer(server_address,RequestHandler(builder)) as httpd:
    #     print(f"Server running on {host}:{port}")
    #     httpd.serve_forever()


# 新线程执行的代码


if __name__ == "__main__":
    # import argparse
    # parser = argparse.ArgumentParser()
    # parser.add_argument("filename", nargs='?', help="mdx file name")
    # args = parser.parse_args()

    # # use GUI to select file, default to extract
    # if not args.filename:
    #     root = tk.Tk()
    #     root.withdraw()
    #     args.filename = filedialog.askopenfilename(parent=root)

    # if not os.path.exists(args.filename):
    #     print("Please specify a valid MDX/MDD file")
    # else:
    filename = "D:/dicts/Eng/olad10/Oxford Advanced Learner's Dictionary 10th.mdx"
    jp_path1 = "D:/dicts/ja/xsjrihanshuangjie/"
    jp_path2 = "D:/dicts/ja/Shogakukanjcv3/"
    en_builder = IndexBuilder(filename)
    filename_jp1 = "D:/dicts/ja/xsjrihanshuangjie/xsjrihanshuangjie.mdx"
    filename_jp2 = "D:/dicts/ja/Shogakukanjcv3/Shogakukanjcv3.mdx"
    jp_builder1 = IndexBuilder(filename_jp1)
    jp_builder2 = IndexBuilder(filename_jp2)

    # t = threading.Thread(target=loop, args=())
    jp_local = get_local_resource([Path(jp_path1), Path(jp_path2)])
    pattern_t = re.compile(r"@@@LINK=(.*)")
    # import ipdb
    # ipdb.set_trace()
    # r=builder.mdx_lookup('花')
    # print('h')
    thread1 = threading.Thread(target=run_server, args=(en_builder, {}, 8000))
    thread2 = threading.Thread(
        target=run_server, args=(jp_builder1, jp_local, 8002, jp_builder2)
    )

    # Start both threads
    thread1.start()
    thread2.start()

    # Wait for both threads to finish
    thread1.join()
    thread2.join()
    # run_server(builder)
    # run_server(jp_builder,8002)
    # t.start()
