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

log_util.enable_debug(False)


CHINESE_PUNCTUATIONS = (
    r"！？｡。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏.\n"
)


class MandarinParser(AbstractParser):
    """
    Using jieba to parse the Mandarin
    """

    def __init__(self):
        super().__init__()
        self.user_dict = {}
        self.dict_loaded = False
        self._cache = {}

    def load_dict_from_file(self):
        dict_path = os.path.join(
            current_app.env_config.datapath,
            f"mandarin.user_dict.txt",
        )
        if not os.path.exists(dict_path):
            return
        zws = "\u200B"
        with open(dict_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        od = OrderedDict()
        for term in lines:
            if term.strip() == "":
                continue
            key = term.replace(",", "").strip()
            od[key] = term.strip().split(",")

        self.load_dict(od)

    def load_dict(self, dict_set):
        if dict_set and not self.dict_loaded:
            self.user_dict = dict_set
            MandarinParser._seg.dict_force = dict_set
        print("Dict loaded.")
        self.dict_loaded = True

    def update_dict(self, od: dict):
        self.user_dict.update(od)
        MandarinParser._seg.dict_force = self.user_dict

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

    @classmethod
    def name(cls):
        return "Mandarin"

    def parse_para(self, para_text):
        """
        Parsing the paragraph
        """
        para_result = []
        for tok in MandarinParser._seg(para_text):
            is_word = tok not in CHINESE_PUNCTUATIONS
            _pinyin = ""
            if is_word:
                _pinyin_list = list(chain.from_iterable(pinyin(tok)))
                _pinyin = "".join(_pinyin_list) + " "
            para_result.append((tok, is_word, _pinyin))
        return para_result

    def get_parsed_tokens(self, text: str, language) -> List:
        """
        Parsing the text by paragraph, then generate the ParsedToken List,
        for the correct token order.
        cached the parsed result
        """
        self.load_dict_from_file()
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
            is_eos = tok == "¶"

            res.append(ParsedToken(tok, is_word, is_eos, None, _pinyin))

        return res

    def is_dict_loaded(self):
        return self.dict_loaded

    def get_user_dict(self):
        return self.user_dict
