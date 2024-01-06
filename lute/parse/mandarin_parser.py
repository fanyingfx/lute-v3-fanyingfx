"""
Default using jieba to parse Chinese.
https://github.com/fxsjy/jieba

"""
import os
from collections import OrderedDict
from typing import List
from functools import lru_cache
from itertools import chain

from flask import current_app
from pypinyin import pinyin
from lute.parse.base import AbstractParser
from lute.parse.base import ParsedToken
import importlib
from hanlp.utils import log_util

from cachetools import cached
from cachetools.keys import hashkey

from lute.parse.user_dicts import load_from_db, load_from_file

log_util.enable_debug(False)


CHINESE_PUNCTUATIONS = (
    r"！？｡。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏.\n"
)


class MandarinParser(AbstractParser):
    """
    Using hanlp to parse the Mandarin
    """

    def __init__(self):
        super().__init__()
        self.user_dict = {}
        self.dict_loaded = False
        self._cache = {}

    def full_load_dict(self, language):
        if self.dict_loaded:
            return

        ud = load_from_db(language)
        udf = load_from_file(language)
        ud.update(udf)
    # else:
        #     od = load_from_file(language)

        self.reload_dict(ud)
        self.dict_loaded = True

    def reload_dict(self, dict_set):
        if dict_set:
            self.user_dict = dict_set
            # MandarinParser._seg.dict_force = dict_set.copy()

    def update_dict(self, od=None):
        if od:
            self.user_dict.update(od)
            # MandarinParser._seg.dict_force = self.user_dict.copy()

    @classmethod
    @lru_cache()
    def is_supported(cls):
        """
        Using lru_cache to make the test execution run fast,
        otherwise the test execution will run very slowly,
        the process of checking whether the hanlp package is installed can be slow.
        If hanlp is not installed, using jieba as default chinese parser.
        """
        is_supported = False
        if importlib.util.find_spec("hanlp"):
            hanlp = importlib.import_module("hanlp")
            MandarinParser._seg = hanlp.load(hanlp.pretrained.tok.FINE_ELECTRA_SMALL_ZH)
            is_supported = True

        return is_supported
    def get_hashable(self):
        return tuple((k,tuple(v)) for k,v in self.user_dict.items())


    @classmethod
    def name(cls):
        return "Mandarin"

    @cached(
        cache={},
        key=lambda self, para_text : hashkey(self.get_hashable(), para_text)
    )
    def parse_para(self, para_text):
        """
        Parsing the paragraph
        """
        para_result = []
        MandarinParser._seg.dict_force = self.user_dict
        for tok in MandarinParser._seg(para_text):
            is_word = tok not in CHINESE_PUNCTUATIONS
            _pinyin = ""
            if is_word:
                _pinyin_list = list(chain.from_iterable(pinyin(tok)))
                _pinyin = "".join(_pinyin_list) + " "
            para_result.append((tok, is_word, _pinyin))
        return para_result

    @cached(
        cache={},
        key=lambda self, para_text,*args: hashkey(self.get_hashable(), para_text)
    )
    def get_parsed_tokens(self, text: str, language) -> List:
        """
        Parsing the text by paragraph, then generate the ParsedToken List,
        for the correct token order.
        cached the parsed result
        """
        self.full_load_dict(language)
        tokens = []
        for para in text.split("\n"):
            para = para.strip()
            tokens.extend(self.parse_para(para))
            tokens.append(["¶", False, ""])
        # Remove the trailing ¶
        # by stripping it from the result
        tokens.pop()
        res = []
        for tok, is_word, _pinyin in tokens:
            is_eos = tok == "¶" or tok in language.regexp_split_sentences

            res.append(ParsedToken(tok, is_word, is_eos, tok, _pinyin))

        return res

    def is_dict_loaded(self):
        return self.dict_loaded

    def get_user_dict(self):
        return self.user_dict

    def delete_from_user_dict(self, k, v):
        if k in self.user_dict and v == self.user_dict[k]:
            self.user_dict.pop(k)
            self.reload_dict(self.user_dict.copy())
