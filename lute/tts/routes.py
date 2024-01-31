import os

from flask import Blueprint
from flask import current_app
from flask import jsonify
from flask import request
from flask import send_from_directory

from lute.tts.edge_tts_service import gen_text_filename
from lute.tts.edge_tts_service import save_sound

bp = Blueprint("tts", __name__, url_prefix="/tts")
import asyncio


def save_sound_sync(text, filepath):
    asyncio.run(save_sound(text, filepath))


@bp.post("/genaudio/<bookid>")
def gen_audio(bookid):
    text = request.json.get("text")
    # filepath =
    datapath = current_app.config["DATAPATH"]
    directory = os.path.join(datapath, "bookttsaudios", str(bookid))
    if not os.path.isdir(directory):
        os.makedirs(directory)
    filename = gen_text_filename(text)
    filepath = os.path.join(directory, filename)
    res = {"status": 0}
    res["filename"] = None
    res["bookid"] = str(bookid)
    if text and text.strip() != "":
        try:
            save_sound_sync(text, filepath)
            res["status"] = 1
            res["filename"] = filename
        except Exception as e:
            print(e)

    return jsonify(res)


@bp.get("/<bookid>/<filename>")
def get_audio(bookid, filename):
    # text = request.json.get('text')
    # save_sound_sync(text)
    datapath = current_app.config["DATAPATH"]
    directory = os.path.join(datapath, "bookttsaudios", str(bookid))
    # filename = gen_text_filename(text)
    # print(directory, img_name)
    return send_from_directory(directory, filename)

    # res={'translation': baidu_translate(text)}
    # return jsonify(res)
