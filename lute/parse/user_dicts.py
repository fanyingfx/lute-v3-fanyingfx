from collections import OrderedDict

from flask import current_app

from lute.db import db
from lute.models.term import Term
import os

ZWS = "\u200B"


def get_terms_from_db(language):
    terms = db.session.query(Term).filter(
        Term.language == language,
        Term.token_count > 1,
    ).all()

    return [term.text for term in terms]


def load_from_db(language):
    terms = get_terms_from_db(language)
    ud = OrderedDict()
    for term in terms:
        word = term.replace(ZWS, '')
        ud[word] = term.strip().split(ZWS)

    return ud


def load_from_file(language):
    dict_path = get_dict_path(language)
    if not os.path.exists(dict_path) or os.stat(dict_path).st_size < 2:
        f = open(dict_path, "w", encoding="utf-8")
        f.close()
        return {}

    with open(dict_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    odf = OrderedDict()
    for term in lines:
        if term.strip() == "":
            continue
        key = term.replace(",", "").replace('，', '').strip()
        odf[key] = term.strip().replace('，', ',').split(",")
    return odf


def _write_ud_to_file(ud, dict_path):
    res = []
    for _, v in ud.items():
        res.append(",".join(v))
    with open(dict_path, "w", encoding="utf-8") as f:
        f.write("\n".join(res))


def get_dict_path(language):
    return os.path.join(
        current_app.env_config.datapath,
        f"{language.parser.name().replace(' ', '').lower()}.user_dict.txt",
    )


def delete_from_user_dict(term):
    language = term.language
    k = term.text_lc.replace(ZWS, "")
    v = term.text_lc.split(ZWS)
    language.parser.delete_from_user_dict(k, v)


def update_user_dict(language, od):
    language.parser.update_dict(od)
