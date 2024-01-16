from flask import Blueprint,jsonify

from lute.translation.services import baidu_translate

bp = Blueprint("trans", __name__, url_prefix="/trans")


@bp.get('/baidu/<text>')
def baidutrans(text):
    res={'translation': baidu_translate(text)}
    return jsonify(res)
