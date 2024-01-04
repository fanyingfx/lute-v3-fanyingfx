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

    # dict_path = get_dict_path(language)

    # if not os.path.exists(dict_path) or os.stat(dict_path).st_size < 2:
    terms = get_terms_from_db(language)
    ud = {}
    for term in terms:
        # lines.append(term.replace(ZWS, ","))
        # word_list=term.strip().split(ZWS)
        word = term.replace(ZWS,'')
        ud[word] = term.strip().split(ZWS)

        # with open(dict_path, "w", encoding="utf-8") as f:
        #     f.write("\n".join(lines))

    return ud

def load_from_file(language):
    dict_path = get_dict_path(language)
    if not os.path.exists(dict_path) or os.stat(dict_path).st_size < 2:
        f = open(dict_path, "w", encoding="utf-8")
        f.close()
        return {}

    with open(dict_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    odf = {}
    for term in lines:
        if term.strip() == "":
            continue
        key = term.replace(",", "").strip()
        odf[key] = term.strip().split(",")
    return odf



# def load_user_dict(language):
#     dict_path = get_dict_path(language)
#     if not os.path.exists(dict_path) or os.stat(dict_path).st_size < 2:
#         terms = get_terms_from_db(language)
#         lines = []
#         for term in terms:
#             lines.append(term.replace(ZWS, ","))
#
#         with open(dict_path, "w", encoding="utf-8") as f:
#             f.write("\n".join(lines))
#     else:
#         with open(dict_path, "r", encoding="utf-8") as f:
#             lines = f.readlines()
#         lines = [term.strip() for term in lines]
#     od = OrderedDict()
#     for word in lines:
#         od[word] = word.strip().split(",")
#
#     language.parser.load_dict(od)
#

def _write_ud_to_file(ud, dict_path):
    res = []
    for _, v in ud.items():
        res.append(",".join(v))
    with open(dict_path, "w", encoding="utf-8") as f:
        f.write("\n".join(res))


def get_dict_path(language):
    return os.path.join(
        current_app.env_config.datapath,
        f"{language.parser.name().replace(' ','').lower()}.user_dict.txt",
    )


def delete_from_user_dict(term):
    language = term.language
    k = term.text_lc.replace(ZWS, "")
    v = term.text_lc.split(ZWS)
    # dict_path = get_dict_path(language)
    language.parser.delete_from_user_dict(k, v)
    # ud = language.parser.get_user_dict()
    # _write_ud_to_file(ud, dict_path)


def update_user_dict(language, od):
    # dict_path = get_dict_path(language)
    language.parser.update_dict(od)
    # ud = language.parser.get_user_dict()
    # _write_ud_to_file(ud, dict_path)
