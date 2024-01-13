from flask import (
    Blueprint,
    make_response,
    request,
)
from lute.mdx_server.mdx_server import (
    MDXDict,
    IndexBuilder,
    get_local_resource,
    Path,
    content_type_map,
)

bp = Blueprint("dict", __name__, url_prefix="/dict")
en_dir1 = "/home/fan/dicts/Eng/olad10"
en_filename1 = "Oxford Advanced Learner's Dictionary 10th.mdx"
en_dir2 = "/home/fan/dicts/Eng/mwal"
en_filename2 = "Merrian Webster Advanced Learners_new.mdx"
en_dir3 = "/home/fan/dicts/Eng/MWnow"
en_filename3 = "mw_now.mdx"
jp_filedir = "/home/fan/dicts/ja/Shogakukanjcv3"
jp_filename1 = "Shogakukanjcv3.mdx"
jp_filename2 = "xsjrihanshuangjie.mdx"
jp_dir2 = "/home/fan/dicts/ja/xsjrihanshuangjie"
jp_filename3 = "NHK日本語発音アクセント辞書.mdx"
jp_dir3 = "/home/fan/dicts/ja/nhk"
en_res1 = Path(en_dir1)
en_res2 = Path(en_dir2)
en_res3 = Path(en_dir3)
jp_res1 = Path(jp_filedir)
jp_res2 = Path(jp_dir2)
jp_res3 = Path(jp_dir3)

dict_local = get_local_resource([en_res1, en_res2, en_res3, jp_res1, jp_res2, jp_res3])

en_builder1 = IndexBuilder(f"{en_dir1}/{en_filename1}")
en_builder2 = IndexBuilder(f"{en_dir2}/{en_filename2}")
en_builder3 = IndexBuilder(f"{en_dir3}/{en_filename3}")
jp_builder = IndexBuilder(f"{jp_filedir}/{jp_filename1}")
jp_builder2 = IndexBuilder(f"{jp_dir2}/{jp_filename2}")
jp_builder3 = IndexBuilder(f"{jp_dir3}/{jp_filename3}")

en_bd1 = MDXDict(en_builder1, dict_local)
en_bd2 = MDXDict(en_builder2, dict_local)
en_bd3 = MDXDict(en_builder3, dict_local)
jp_bd1 = MDXDict(jp_builder, dict_local)
jp_bd2 = MDXDict(jp_builder2, dict_local)
jp_bd3 = MDXDict(jp_builder3, dict_local, "jp3")


def handle_req(filename, loc):
    ext = filename.split(".")[-1]
    content_type = content_type_map.get(ext, content_type_map["html"])
    if filename in loc:
        content = loc[filename]
    else:
        for abd in [en_bd1, en_bd2, en_bd3, jp_bd1, jp_bd2, jp_bd3]:
            content = abd.lookup(f"/{filename}")
            if content != b"":
                break
        if ext in content_type_map:
            loc[filename] = content
    response = make_response(content)
    response.headers["Content-Type"] = content_type
    response.headers["Cache-Control"] = "max-age=604800, must-revalidate"
    response.headers.add("Access-Control-Allow-Origin", "*")

    return response


@bp.route("/", defaults={"path": ""})
@bp.route("/<path:path>")
def index(path):
    # print("path", path)
    return handle_req(path, dict_local)


@bp.route("/en")
def query_en():
    word = request.args.get("word", "")
    ext = word.split(".")[-1]
    if ext in content_type_map:
        return handle_req(word, dict_local)
    for ebd in [en_bd1, en_bd2, en_bd3]:
        res = ebd.lookup(word)
        if res != b"":
            break
    response = make_response(res)
    content_type = content_type_map["html"]
    response.headers["Content-type"] = content_type
    response.headers["Cache-Control"] = "max-age=604800, must-revalidate"
    return response


@bp.route("/jp")
def query_jp():
    word = request.args.get("word", "")
    ext = word.split(".")[-1]
    if ext in content_type_map:
        return handle_req(word, dict_local)
    pronunciation = jp_bd3.lookup(word)

    for jbd in [jp_bd1, jp_bd2]:
        res = jbd.lookup(word)
        if res != b"":
            break
    res = pronunciation + b"<br/>" + res
    response = make_response(res)
    content_type = content_type_map["html"]
    response.headers["Content-type"] = content_type
    response.headers["Cache-Control"] = "max-age=604800, must-revalidate"

    return response
