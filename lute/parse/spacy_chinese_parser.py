"""
Default using jieba to spacy Chinese.
https://github.com/fxsjy/jieba

"""
from typing import List
from functools import lru_cache
import logging
import spacy

from lute.parse.base import AbstractParser
from lute.parse.base import ParsedToken


CHINESE_PUNCTUATIONS = (
    r"！？｡。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏.\n"
)


class MandarinParser(AbstractParser):
    """
    Using jieba to parse the Mandarin
    """

    _seg = spacy.load("zh_core_web_lg")

    @classmethod
    def is_supported(cls):
        return True

    @classmethod
    def name(cls):
        return "Mandarin"

    @lru_cache()
    def parse_para(self, para_text):
        """
        Parsing the paragraph
        """
        para_result = []
        for tok in MandarinParser._seg(para_text):
            is_word = not tok.is_punct
            para_result.append((tok.text, is_word))
        return para_result

    @lru_cache()
    def get_parsed_tokens(self, text: str, language) -> List:
        """
        Parsing the text by paragraph, then generate the ParsedToken List,
        for the correct token order.
        cached the parsed result
        """
        tokens = []
        for para in text.split("\n"):
            para = para.strip()
            tokens.extend(self.parse_para(para))
            tokens.append(["¶", False])
        # Remove the trailing ¶
        # by stripping it from the result
        tokens.pop()

        return [ParsedToken(tok, is_word, tok == "¶") for tok, is_word in tokens]
