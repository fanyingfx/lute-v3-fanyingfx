from flask import (
    Blueprint,
    current_app,
    render_template,
    redirect,
    url_for,
    flash,
    make_response,
    request,
)
from urllib.parse import urlparse, parse_qs, unquote, unquote_plus
from lute.mdx_server.mdx_server import (
    MDXDict,
    IndexBuilder,
    get_local_resource,
    Path,
    content_type_map,
)

bp = Blueprint("dict", __name__, url_prefix="/dict")
filedir = "/home/fan/dicts/Eng/olad10"
filename = "Oxford Advanced Learner's Dictionary 10th.mdx"
jp_filedir = "/home/fan/dicts/ja/Shogakukanjcv3"
jp_filename = "Shogakukanjcv3.mdx"
resource_path = Path(filedir)
jp_resource_path = Path(jp_filedir)

en_local = get_local_resource([resource_path, jp_resource_path])
jp_local = get_local_resource([jp_resource_path])

builder = IndexBuilder(f"{filedir}/{filename}")
jp_builder = IndexBuilder(f"{jp_filedir}/{jp_filename}")

bd = MDXDict(builder, en_local)
jp_bd = MDXDict(jp_builder, jp_local)


def handle_req(filename, loc):
    ext = filename.split(".")[-1]
    content_type = content_type_map.get(ext, content_type_map["html"])
    if filename in loc:
        content = loc[filename]
    else:
        content = bd.lookup(f"/{filename}")
    response = make_response(content)
    response.headers["Content-Type"] = content_type
    return response


@bp.route("/<filename>")
def index(filename):
    print("hell0")
    return handle_req(filename, en_local)


@bp.route("/en/<word>")
def query_en(word):
    ext = word.split(".")[-1]
    if ext in content_type_map:
        return handle_req(word, en_local)
    res = bd.lookup(word)
    response = make_response(res)
    content_type = content_type_map["html"]
    response.headers["Content-type"] = content_type
    return response


@bp.route("/jp")
def query_jp():
    word = request.args.get("word", "")
    ext = word.split(".")[-1]
    if ext in content_type_map:
        return handle_req(word, jp_local)
    res = jp_bd.lookup(word)
    response = make_response(res)
    content_type = content_type_map["html"]
    response.headers["Content-type"] = content_type
    return response
