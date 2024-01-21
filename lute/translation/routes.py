from flask import Blueprint,jsonify,request

from lute.translation.services import baidu_translate
from lute.parse.fugashi_parser import FugashiParser

bp = Blueprint("trans", __name__, url_prefix="/trans")


@bp.post('/baidu')
def baidutrans():
    text = request.json.get('text')
    res={'translation': baidu_translate(text)}
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
