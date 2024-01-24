from flask import Blueprint,jsonify,request

from lute.translation.services import baidu_translate,youdao_translate
from lute.parse.fugashi_parser import FugashiParser
from lute.tts.multiplelang_detect import get_lang

bp = Blueprint("trans", __name__, url_prefix="/trans")


@bp.post('/baidu')
def trans2cn():
    text = request.json.get('text')
    lang=get_lang(text)
    if lang == 'ja':
        trans=youdao_translate(text)
    else:
        trans = baidu_translate(text)
    res={'translation': trans}
    return jsonify(res)

@bp.post('/ana')
def japanese_analysis():
    text = request.json.get('text')
    try:
        ana ='\n'.join(FugashiParser.analyse(text))
    except:
        ana = 'analysis failed'
    res ={'ana':ana}
    return jsonify(res)
