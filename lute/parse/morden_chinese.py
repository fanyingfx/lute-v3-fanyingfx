from typing import List

from lute.parse.base import AbstractParser
from lute.parse.base import ParsedToken
import jieba

jieba.enable_paddle()
# Chinese_
CHINESE_PUNCTS = (
    r"！？｡＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏.\n"
)


class MordenChineseParser(AbstractParser):
    @classmethod
    def name(cls):
        return "MordenChinese"

    def get_parsed_tokens(self, text: str, language) -> List:
        l = []
        for tok in jieba.cut(text, cut_all=False):
            is_word = tok not in CHINESE_PUNCTS
            l.append(ParsedToken(tok, is_word, lemma=tok))
        return l
