from flask import Blueprint,jsonify,request

from lute.translation.services import baidu_translate

bp = Blueprint("trans", __name__, url_prefix="/trans")


@bp.post('/baidu')
def baidutrans():
    text = request.json.get('text')
    res={'translation': baidu_translate(text)}
    return jsonify(res)
