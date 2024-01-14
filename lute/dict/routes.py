import os
from typing import List

from flask import (
    Blueprint,
    make_response,
    request,
current_app
)
from lute.mdx_server.mdx_server import (
    MDXDict,
    IndexBuilder,
    get_local_resource,
    Path,
    content_type_map,
)
from lute.dict.services import load_mdxdict_config

bp = Blueprint("dict", __name__, url_prefix="/dict")
en_dict_pairs=[
    ("C:/Users/fan/Data/dicts/olad10","Oxford Advanced Learner's Dictionary 10th.mdx")
]
d=load_mdxdict_config()
rootfolder=d['rootfolder']
en_dict_conf=d['dicts']['English']
jp_dict_conf = d['dicts']['Japanese']
def get_local_paths(rootfolder,dict_conf):
    root_path=Path(rootfolder)
    dir_name = dict_conf['dir_name']
    root_path = root_path / dir_name
    dictdir_list=dict_conf['dict_list']
    if dict_conf.get('pronunciation'):
        dictdir_list.append(dict_conf['pronunciation'])
    return [root_path / dictdir for dictdir in dictdir_list]
en_local_paths = get_local_paths(rootfolder,en_dict_conf)
jp_local_paths = get_local_paths(rootfolder,jp_dict_conf)
dict_local = get_local_resource(en_local_paths+jp_local_paths)


# en_dir1 = "/home/fan/dicts/Eng/olad10"
# en_filename1 = "Oxford Advanced Learner's Dictionary 10th.mdx"
# en_dir2 = "/home/fan/dicts/Eng/mwal"
# en_filename2 = "Merrian Webster Advanced Learners_new.mdx"
# en_dir3 = "/home/fan/dicts/Eng/MWnow"
# en_filename3 = "mw_now.mdx"
# jp_filedir ="C:/Users/fan/Data/dicts/Shogakukanjcv3"
# jp_filename1 = "Shogakukanjcv3.mdx"
# jp_filename2 = "xsjrihanshuangjie.mdx"
# jp_dir2 = "C:/Users/fan/Data/dicts/xsjrihanshuangjie"
# jp_filename3 = "NHK日本語発音アクセント辞書.mdx"
# jp_dir3 = "C:/Users/fan/AppData/Local/dicts/ja/nhk"
# en_res1 = Path(en_dir1)
# en_res2 = Path(en_dir2)
# en_res3 = Path(en_dir3)
# jp_res1 = Path(jp_filedir)
# jp_res2 = Path(jp_dir2)
# jp_res3 = Path(jp_dir3)
# en_dirs = [Path(dire) for dire, _ in en_dict_pairs]

# dict_local = get_local_resource(en_dirs+[jp_res1, jp_res2,jp_res3])

def find_mdx_file(mdx_folder:Path):
    for file in mdx_folder.iterdir():
        if file.suffix == ".mdx":
            return str(file.absolute())
def get_MDXDicts(rootfolder,dict_conf,dict_local):
    dictdir_list=dict_conf['dict_list']
    rootpath:Path = Path(rootfolder)
    dir_name = dict_conf['dir_name']
    rootpath = rootpath / dir_name
    res=[]
    for dictdir in dictdir_list:
        dir_path:Path =rootpath /dictdir
        mdx_file = find_mdx_file(dir_path)
        idxbd = IndexBuilder(mdx_file)
        res.append(MDXDict(idxbd,dict_local))
    pronunciation_MDXDict = None
    if dict_conf['pronunciation']:
        pronun_path  = rootpath / dict_conf['pronunciation']
        mdx_file = find_mdx_file(pronun_path)
        pronunciation_builder = IndexBuilder(mdx_file)
        pronunciation_MDXDict = MDXDict(pronunciation_builder,dict_local)

    return res,pronunciation_MDXDict









en_bds,_ = get_MDXDicts(rootfolder,en_dict_conf,dict_local)
jp_bds,jp_pronun_bd = get_MDXDicts(rootfolder,jp_dict_conf,dict_local)

# en_ibuilders: List[IndexBuilder] = [ IndexBuilder(f"{dir}/{filename}") for dir ,filename in en_dict_pairs]
# en_builder1 = IndexBuilder(f"{en_dir1}/{en_filename1}")
# en_builder2 = IndexBuilder(f"{en_dir2}/{en_filename2}")
# en_builder3 = IndexBuilder(f"{en_dir3}/{en_filename3}")
# jp_builder = IndexBuilder(f"{jp_filedir}/{jp_filename1}")
# jp_builder2 = IndexBuilder(f"{jp_dir2}/{jp_filename2}")
# jp_builder3 = IndexBuilder(f"{jp_dir3}/{jp_filename3}")

# en_bd1 = MDXDict(en_builder1, dict_local)
# en_bd2 = MDXDict(en_builder2, dict_local)
# en_bd3 = MDXDict(en_builder3, dict_local)
# en_bds = [MDXDict(builder,dict_local) for builder in en_ibuilders  ]
# jp_bd1 = MDXDict(jp_builder, dict_local)
# jp_bd2 = MDXDict(jp_builder2, dict_local)
# jp_bd3 = MDXDict(jp_builder3, dict_local, "jp3")


def handle_req(filename, loc):
    ext = filename.split(".")[-1]
    content_type = content_type_map.get(ext, content_type_map["html"])
    if filename in loc:
        content = loc[filename]
    else:
        for abd in en_bds+jp_bds:
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
    for ebd in en_bds:
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
    print(word)
    ext = word.split(".")[-1]
    if ext in content_type_map:
        return handle_req(word, dict_local)
    pronunciation = jp_pronun_bd.lookup(word)
    # pronunciation = b""

    for jbd in jp_bds:
        res = jbd.lookup(word)
        if res != b"":
            break
    res = pronunciation + b"<br/>" + res
    response = make_response(res)
    content_type = content_type_map["html"]
    response.headers["Content-type"] = content_type
    response.headers["Cache-Control"] = "max-age=604800, must-revalidate"

    return response
