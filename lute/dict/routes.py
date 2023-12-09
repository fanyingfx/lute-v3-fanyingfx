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
en_filename = "Oxford Advanced Learner's Dictionary 10th.mdx"
jp_filedir = "/home/fan/dicts/ja/Shogakukanjcv3"
jp_filename = "Shogakukanjcv3.mdx"
jp_filename2 = "xsjrihanshuangjie.mdx"
jp_dir2 = "/home/fan/dicts/ja/xsjrihanshuangjie"
resource_path = Path(filedir)
jp_resource_path = Path(jp_filedir)
jp_res2 = Path(jp_dir2)

dict_local = get_local_resource([resource_path, jp_resource_path, jp_res2])
# jp_local = get_local_resource([jp_resource_path])

builder = IndexBuilder(f"{filedir}/{en_filename}")
jp_builder = IndexBuilder(f"{jp_filedir}/{jp_filename}")
jp_builder2 = IndexBuilder(f"{jp_dir2}/{jp_filename2}")

bd = MDXDict(builder, dict_local)
jp_bd = MDXDict(jp_builder, dict_local)
jp_bd2 = MDXDict(jp_builder2, dict_local)


def handle_req(filename, loc):
    ext = filename.split(".")[-1]
    content_type = content_type_map.get(ext, content_type_map["html"])
    if filename in loc:
        content = loc[filename]
    else:
        for abd in [bd, jp_bd]:
            content = abd.lookup(f"/{filename}")
            if content != b"":
                break
    response = make_response(content)
    response.headers["Content-Type"] = content_type
    return response


@bp.route("/", defaults={"path": ""})
@bp.route("/<path:path>")
def index(path):
    print("path", path)
    return handle_req(path, dict_local)


@bp.route("/en/<word>")
def query_en(word):
    ext = word.split(".")[-1]
    if ext in content_type_map:
        return handle_req(word, dict_local)
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
        return handle_req(word, dict_local)
    for jbd in [jp_bd, jp_bd2]:
        res = jbd.lookup(word)
        if res != b"":
            break
    response = make_response(res)
    content_type = content_type_map["html"]
    response.headers["Content-type"] = content_type
    return response
