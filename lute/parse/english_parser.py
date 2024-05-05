"""
Parsing for space-delimited languages.

The parser uses some Language settings (e.g., word characters) to
perform the actual parsing.

Includes classes:

- SpaceDelimitedParser
- Turkish
"""

import re
from functools import lru_cache
from typing import List
from lute.parse.base import ParsedToken, AbstractParser
import spacy

from lute.parse.base import RawToken

nlp = spacy.load("en_core_web_sm")


class EnglishParser(AbstractParser):
    """
    A general parser for space-delimited languages,
    such as English, French, Spanish ... etc.
    """

    @classmethod
    def name(cls):
        return "English"

    def __init__(self):
        self.cache = {}
        self.nlp_cache = {}

    def get_parsed_tokens(self, text: str, language) -> List[ParsedToken]:
        "Return parsed tokens."
        clean_text = re.sub(r" +", " ", text)
        zws = chr(0x200B)  # zero-width space
        clean_text = clean_text.replace(zws, "")
        return self._parse_to_tokens(clean_text, language)

    def preg_match_capture(self, pattern, subject):
        """
        Return the matched text and their start positions in the subject.

        E.g. search for r'cat' in "there is a CAT and a Cat" returns:
        [['CAT', 11], ['Cat', 21]]
        """
        matches = re.finditer(pattern, subject, flags=re.IGNORECASE)
        result = [[match.group(), match.start()] for match in matches]
        return result

    @lru_cache()
    def _parse_to_tokens(self, text: str, lang):
        """
        Returns ParsedToken array for given language.
        """
        # replacements = lang.character_substitutions.split("|")
        # for replacement in replacements:
        #     fromto = replacement.strip().split("=")
        #     if len(fromto) >= 2:
        #         rfrom = fromto[0].strip()
        #         rto = fromto[1].strip()
        #         text = text.replace(rfrom, rto)

        text = text.replace("\r\n", "\n")
        text = text.replace("{", "[")
        text = text.replace("}", "]")

        tokens = []
        paras = text.split("\n")
        pcount = len(paras)
        EOP = RawToken("¶", False, True, "")

        for i, para in enumerate(paras):
            if para.startswith("<img"):
                # TODO for img
                # img_src = para.replace("<img=", "")
                img_src = para + "\n"
                tokens.append(RawToken(img_src, False, None, None))
            else:
                tokens.extend(self.parse_para(para, lang))
                if i != (pcount - 1):
                    tokens.append(RawToken("¶", False, True, ""))
        ## pop the last "¶"
        if tokens and tokens[-1] == EOP:
            tokens.pop()

        res = [
            ParsedToken(tok.token, tok.is_word, tok.is_end_of_sent, tok.lemma)
            for tok in tokens
        ]
        return res

    @lru_cache()
    def parse_para(self, text: str, lang):
        """
        Parse a string, appending the tokens to the list of tokens.
        """

        toks = []
        if " " not in text.strip():
            return [RawToken(text, True, False, text)]
        doc = nlp(text)

        for tok in doc:
            toks.append(
                RawToken(tok.text, not tok.is_punct, tok.is_sent_end, tok.lemma_)
            )
            if tok.whitespace_ != "":
                toks.append(RawToken(tok.whitespace_, False, False, ""))
        return toks
