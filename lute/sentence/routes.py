import os
import csv
from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    redirect,
    current_app,
    send_file,
)
from lute.models.language import Language
from lute.models.term import Term as DBTerm
from lute.sentence.service import get_all_sentencenotes
from lute.utils.data_tables import DataTablesFlaskParamParser
from lute.term.datatables import get_data_tables_list
from lute.term.model import Repository, Term
from lute.db import db
from lute.term.forms import TermForm
import lute.utils.formutils
from lute.parse.user_dicts import delete_from_user_dict, update_user_dict
import json

bp = Blueprint("sentence", __name__, url_prefix="/sentence")


@bp.get("/sentencenotes")
def render_sentencenotes():
    return render_template("sentence/sentencenotes.html")


@bp.get("/sentencenotes/data")
def get_sentencenotes():
    all_sentence_notes = get_all_sentencenotes(db.session)
    return jsonify(all_sentence_notes)
