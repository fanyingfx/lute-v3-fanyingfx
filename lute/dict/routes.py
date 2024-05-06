from flask import (
    Blueprint,
    request,
)
from lute.dict.mdxservice import en_query, jp_query

bp = Blueprint("dict", __name__, url_prefix="/dict")
querys = [en_query, jp_query]


# def handle_req(filename, loc):
#     ext = filename.split(".")[-1]
#     content_type = content_type_map.get(ext, content_type_map["html"])
#     if filename in loc:
#         content = loc[filename]
#     else:
#         for abd in en_bds + jp_bds:
#             content = abd.lookup(f"/{filename}")
#             if content != b"":
#                 break
#         if ext in content_type_map:
#             loc[filename] = content
#     response = make_response(content)
#     response.headers["Content-Type"] = content_type
#     response.headers["Cache-Control"] = "max-age=604800, must-revalidate"
#     response.headers.add("Access-Control-Allow-Origin", "*")

#     return response


@bp.route("/", defaults={"path": ""})
@bp.route("/<path:path>")
def index(path):
    for query in querys:
        res = query(path)
        if res != b"":
            return res


@bp.route("/en")
def query_en():
    word = request.args.get("word")
    if word is None:
        return b"Word not found"
    return en_query(word)
    # content_type = content_type_map["html"]
    # response.headers["Content-type"] = content_type
    # response.headers["Cache-Control"] = "max-age=604800, must-revalidate"
    # return response


@bp.route("/jp")
def query_jp():
    word = request.args.get("word")
    if word is None:
        return b""
    return jp_query(word)
    # return en_query(word)
    # word = request.args.get("word", "")
    # ext = word.split(".")[-1]
    # if ext in content_type_map:
    #     return handle_req(word, dict_local)
    # pronunciation = jp_pronun_bd.lookup(word)
    # res = b""
    # for jbd in jp_bds:
    #     res = jbd.lookup(word)
    #     if res != b"":
    #         break
    # res = pronunciation + b"<br/>" + res
    # response = make_response(res)
    # content_type = content_type_map["html"]
    # response.headers["Content-type"] = content_type
    # response.headers["Cache-Control"] = "max-age=604800, must-revalidate"

    # return response
