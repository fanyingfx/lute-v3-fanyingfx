from collections import OrderedDict

from flask import current_app

from lute.db import db
from lute.models.term import Term
import os


def get_terms_from_db(language):
    words = (
        db.session.query(Term)
        .filter(
            Term.language == language,
            Term.token_count > 1,
        )
        .all()
    )
    return words


def load_user_dict(language):
    dict_path = os.path.join(
        current_app.env_config.datapath,
        f"{language.parser.name().replace(' ','').lower()}.user_dict.txt",
    )
    zws = "\u200B"
    if not os.path.exists(dict_path):
        terms = get_terms_from_db(language)
        lines = []
        for term in terms:
            lines.append(term.replace(zws, ","))

        with open(dict_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
    else:
        with open(dict_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    od = OrderedDict()
    for word in lines:
        od[word] = word.strip().split(",")

    language.parser.load_dict(od)


def update_user_dict(language, od):
    dict_path = os.path.join(
        current_app.env_config.datapath,
        f"{language.parser.name().replace(' ','').lower()}.user_dict.txt",
    )
    language.parser.update_dict(od)
    res = []
    for _, v in language.parser.get_user_dict().items():
        res.append(",".join(v))
    with open(dict_path, "w", encoding="utf-8") as f:
        f.writelines(res)
