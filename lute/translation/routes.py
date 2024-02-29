from flask import Blueprint, jsonify, request
import traceback, sys
from lute.translation.services import baidu_translate, youdao_translate, youdao_status
from lute.parse.fugashi_parser import FugashiParser
from lute.tts.multiplelang_detect import get_lang
from lute.translation.japanese_analyser import get_analyzed_res

bp = Blueprint("trans", __name__, url_prefix="/trans")


@bp.post("/baidu")
def trans2cn():
    text = request.json.get("text")
    lang = get_lang(text)
    if lang == "ja" and youdao_status:
        trans = youdao_translate(text)
    else:
        trans = baidu_translate(text)
    res = {"translation": trans}
    return jsonify(res)


@bp.post("/ana")
def japanese_analysis():
    text = request.json.get("text")
    zws = "\u200b"
    text = text.replace(zws, "")
    try:
        # ana ='\n'.join(FugashiParser.analyse(text))
        ana = get_analyzed_res(text)
    except Exception as e:
        ana = "analysis failed"
        traceback.print_exc(file=sys.stdout)
    res = {"ana": ana}
    return jsonify(res)


@bp.post("/fugashi")
def fugashi_analysis():
    text = request.json.get("text")
    zws = "\u200b"
    text = text.replace(zws, "")
    try:
        ana = "\n".join(FugashiParser.analyse(text))
    except Exception as e:
        ana = "analysis failed"
        traceback.print_exc(file=sys.stdout)
    res = {"ana": ana}
    return jsonify(res)
