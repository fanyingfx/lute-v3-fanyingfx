import re
from typing import List, Any
from typing import List
import jaconv
from lute.parse.base import ParsedToken, AbstractParser
from lute.models.setting import UserSetting
from fugashi import Tagger


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
    _tagger = Tagger("-d /home/fan/.unidics/unidic-csj-202302")
    _cache = {}

    @classmethod
    def is_supported(cls):
        return True

    @classmethod
    def name(cls):
        return "Japanese"

    @classmethod
    def _get_cache(cls, key):
        return FugashiParser._cache.get(key)

    @classmethod
    def _set_cache(cls, key, res):
        FugashiParser._cache[key] = res

    @classmethod
    def parse_para(cls, text: str, language) -> list[list[str | Any] | list[str]]:
        lines = []

        if FugashiParser._get_cache(text):
            return FugashiParser._get_cache(text)
        for tok in FugashiParser._tagger(text.strip()):
            reading_is_kana = tok.feature.kana
            reading = tok.feature.kana
            if reading_is_kana or not reading:
                reading = ""
            else:
                reading = jaconv.kata2hira(reading)
            lines.append(
                [
                    tok.surface,
                    str(tok.char_type),
                    "-1" if tok.is_unk else "0",
                    tok.feature.orthBase,
                    reading,
                ]
            )

        lines.append(["EOP", "3", "7", "8", ""])
        # res = [line_to_token(lin) for lin in lines]

        FugashiParser._set_cache(text, lines)
        return lines

    def get_parsed_tokens(self, text: str, language) -> List[ParsedToken]:
        """
        Parse the string using Sudachi
        """
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
            # all_word_types=['名詞', '記号', '感動詞', '副詞', '形状詞', '補助記号', '接尾辞', '形容詞', '助詞', '連体詞',
            #        '接続詞', '接頭辞', '代名詞', '動詞'
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
    @staticmethod
    def _char_is_hiragana(c) -> bool:
        return "\u3040" <= c <= "\u309F"

    @staticmethod
    def _string_is_hiragana(s: str) -> bool:
        return all(FugashiParser._char_is_hiragana(c) for c in s)

    def _char_is_hiragana(self, c) -> bool:
        return "\u3040" <= c <= "\u309F"

    def get_reading(self, text: str):
        """
        Get the pronunciation for the given text.

        Returns None if the text is all hiragana, or the pronunciation
        doesn't add value (same as text).
        """

        if self._string_is_hiragana(text):
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