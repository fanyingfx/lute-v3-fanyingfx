import re
from functools import lru_cache
from typing import List

import jaconv
from flask import current_app
from fugashi import Tagger

from lute.models.setting import UserSetting
from lute.parse.base import AbstractParser
from lute.parse.base import ParsedToken

# from lute.parse.base import RawToken
from lute.config.app_config import AppConfig

config_file = AppConfig.default_config_filename()
ac = AppConfig(config_file)

kana_pattern = re.compile("[\u3040-\u309f\u30a0-\u30ffー]+")


# TODO using https://github.com/KoichiYasuoka/UniDic2UD to parse Japanese
#
class FugashiParser(AbstractParser):
    """
    Another Japanese Parser, Fugashi which provide wheels for
    Linux, OSX and Win64, not suitable for Win32, can easy using the UniDic
    https://github.com/polm/fugashi
    https://clrd.ninjal.ac.jp/unidic/
    """

    _is_supported = True
    _dict_path = ""
    # Can using -d <dict_path> to using the local unidic,
    # For example
    # _tagger = Tagger("-d /home/fy/.unidics/unidic-csj-202302")
    # unidic can download from  https://clrd.ninjal.ac.jp/unidic/
    # _tagger = Tagger("-d .unidics/unidic-csj-202302")
    _tagger = Tagger(ac.unidic_csj_path)
    _tagger_type = "spoken"
    _ana_tagger = Tagger()
    _w_tagger = Tagger()
    _s_tagger = Tagger()

    @classmethod
    def is_supported(cls):
        return True

    @classmethod
    def name(cls):
        return "Japanese"

    @classmethod
    @lru_cache()
    def parse_para(cls, text: str, language):
        """
        https://clrd.ninjal.ac.jp/unidic/faq.html
        """
        lines = []
        tagger = cls._tagger
        if text.startswith("「"):
            tagger = cls._tagger
        for tok in tagger(text.strip()):
            reading_is_kana = FugashiParser._string_is_kana(tok.surface)
            reading = tok.feature.kana
            is_forein = tok.feature.goshu == "外"
            if is_forein:
                reading = tok.feature.lemma.split("-")[-1]
            elif reading_is_kana or not reading:
                reading = ""
            else:
                reading = jaconv.kata2hira(reading)
            lemma = tok.feature.orthBase
            if reading_is_kana:
                lemma = tok.surface

            lines.append(
                [
                    tok.surface,
                    str(tok.char_type),
                    "-1" if tok.is_unk else "0",
                    # tok.feature.orthBase,
                    lemma,
                    reading,
                ]
            )

        lines.append(["EOP", "3", "7", "8", ""])
        # res = [line_to_token(lin) for lin in lines]

        return lines

    # @lru_cache()
    def get_parsed_tokens(self, text: str, language) -> List[ParsedToken]:
        """ """
        text = re.sub(r"[ \t]+", " ", text).strip()
        lines = []

        for para in text.split("\n"):
            lines.extend(FugashiParser.parse_para(para.rstrip(), language))

        def line_to_token(lin):
            """Convert parsed line to a ParsedToken."""
            term, node_type, third, lemma, reading = lin
            is_eos = term in language.regexp_split_sentences
            if term == "EOP" and third == "7":
                term = "¶"
            is_word = (
                node_type in "2678" and third is not None
            )  # or node_type in "2678"
            if not is_word:
                reading = ""
            return ParsedToken(term, is_word, is_eos, lemma, reading)

        tokens = [line_to_token(lin) for lin in lines]
        return tokens

    # Hiragana is Unicode code block U+3040 - U+309F
    # ref https://stackoverflow.com/questions/72016049/
    #   how-to-check-if-text-is-japanese-hiragana-in-python
    # @staticmethod
    # def _char_is_kana(c) -> bool:
    #     return

    @staticmethod
    def _string_is_kana(s: str) -> bool:
        return bool(kana_pattern.fullmatch(s))

    @classmethod
    def switch_tagger(cls, type="spoken"):
        dict_config = current_app.env_config
        try:
            cls._ana_tagger = Tagger(f"-d {dict_config.userunidic['s']}")
            cls._w_tagger = Tagger(f"-d {dict_config.userunidic['w']}")
            cls._s_tagger = Tagger(f"-d {dict_config.userunidic['s']}")
        except Exception:
            pass

        if type == "spoken":
            cls._tagger = Tagger(f"-d {dict_config.userunidic['s']}")
            cls._tagger_type = "spoken"
        else:
            cls._tagger = Tagger(f"-d {dict_config.userunidic['w']}")
            cls._tagger_type = "writing"

    @classmethod
    def get_reading(cls, text: str):
        """
        Get the pronunciation for the given text.

        Returns None if the text is all hiragana, or the pronunciation
        doesn't add value (same as text).
        """

        if cls._string_is_kana(text):
            return None

        readings = []
        # with MeCab(flags) as nm:
        for tok in FugashiParser._tagger(text):
            readings.append(tok.feature.kana)

        # for n in (text, as_nodes=True):
        #     readings.append(n.feature)
        readings = [r.strip() for r in readings if r is not None and r.strip() != ""]

        ret = "".join(readings).strip()
        if ret in ("", text):
            return None

        jp_reading_setting = UserSetting.get_value("japanese_reading")
        if jp_reading_setting == "katakana":
            return ret
        if jp_reading_setting == "hiragana":
            return jaconv.kata2hira(ret)
        if jp_reading_setting == "alphabet":
            return jaconv.kata2alphabet(ret)
        raise RuntimeError(f"Bad reading type {jp_reading_setting}")

    @classmethod
    def analyse(cls, text):
        print("analysis text", text)
        tagger = cls._tagger
        if text.startswith("「"):
            tagger = cls._s_tagger
        tokens = tagger(text.strip())
        res = []

        def halfwidth_to_fullwidth(text):
            # Define a translation table for half-width to full-width conversion
            halfwidth_chars = "".join(
                chr(i) for i in range(0x0021, 0x007F)
            )  # ASCII characters
            fullwidth_chars = "".join(
                chr(i) for i in range(0xFF01, 0xFF5F)
            )  # Full-width ASCII characters
            translation_table = str.maketrans(halfwidth_chars, fullwidth_chars)

            # Use translate to convert half-width to full-width
            fullwidth_text = text.translate(translation_table)
            return fullwidth_text

        for tok in tokens:
            lemma = tok.feature.lemma
            # orthbase = tok.feature.orthBase
            fws = "\uff0a"  # full-width space
            if tok.feature.goshu == "外":
                lemma = lemma.split("-")[-1]
                lemma = halfwidth_to_fullwidth(lemma)
            pos1 = tok.feature.pos1
            repalce_names = [
                ("補助記号", "記"),
                ("代名詞", "代"),
                ("名詞", "名"),
                ("助詞", "助"),
                ("助動詞", "助動"),
                ("詞", ""),
            ]
            for o, r in repalce_names:
                pos1 = pos1.replace(o, r)
            c_type = tok.feature.cType
            c_form = tok.feature.cForm
            c_type = c_type.replace("*", fws)
            c_form = c_form.replace("*", fws)
            # if c_form=='*' and c_type=='*':
            #     c_form='\u3000'
            #     c_type='\u3000'
            rec = (tok.surface, lemma, pos1, c_type, c_form)
            if all(rec):
                res.append(rec)
        res = []

        def align(text, width):
            full_width_space = "\u3000"
            text_width = len(text)
            text = text.replace("-", "－")
            padding_size = width - text_width
            return text + full_width_space * padding_size

        for rec in res:
            max_len = max([len(c) for c in rec if c is not None])
            new_rec = [align(text, max_len) for text in rec]
            res.append(new_rec)
        transposed_array = list(map(list, zip(*res)))
        new_res = []
        for arr in transposed_array:
            new_res.append("\u3000".join(arr))
        return new_res


if __name__ == "__main__":
    t1 = "と幽かな叫び声をお挙げになった。"
    print(FugashiParser.analyse(t1))
