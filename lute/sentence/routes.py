from flask import (
    Blueprint,
    jsonify,
    render_template,
)
from lute.sentence.service import get_all_sentencenotes
from lute.db import db

bp = Blueprint("sentence", __name__, url_prefix="/sentence")


@bp.get("/sentencenotes/index")
def render_sentencenotes():
    return render_template("sentence/sentencenotes.html")


@bp.get("/sentencenotes")
def get_sentencenotes():
    # #[[sentencenote data]]
    all_sentence_notes = get_all_sentencenotes(db.session)
    return jsonify(all_sentence_notes)
