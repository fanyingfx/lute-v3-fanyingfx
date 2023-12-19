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
from lute.utils.english_lemma import lemmatize_tokens
import spacy

nlp = spacy.load("en_core_web_sm")


class SpaceDelimitedParser(AbstractParser):
    """
    A general parser for space-delimited languages,
    such as English, French, Spanish ... etc.
    """

    @classmethod
    def name(cls):
        return "Space Delimited"

    def __init__(self):
        self.cache = {}
        self.nlp_cache = {}

    def _set_cache(self, k, v):
        self.cache[k] = v

    def _get_from_cache(self, k):
        return self.cache[k]

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

    def _parse_to_tokens(self, text: str, lang):
        """
        Returns ParsedToken array for given language.
        """
        replacements = lang.character_substitutions.split("|")
        for replacement in replacements:
            fromto = replacement.strip().split("=")
            if len(fromto) >= 2:
                rfrom = fromto[0].strip()
                rto = fromto[1].strip()
                text = text.replace(rfrom, rto)

        text = text.replace("\r\n", "\n")
        text = text.replace("{", "[")
        text = text.replace("}", "]")

        tokens = []
        paras = text.split("\n")
        pcount = len(paras)
        for i, para in enumerate(paras):
            # self.parse_para(para, lang, tokens)
            tokens.extend(self.parse_para(para, lang, i))
            if i != (pcount - 1):
                tokens.append(ParsedToken("¶", False, True))

        return tokens

    def parse_para(self, text: str, lang, i):
        """
        Parse a string, appending the tokens to the list of tokens.
        """

        toks = []
        key = f"{i}-{text}"
        if key in self.cache:
            return self._get_from_cache(key)
        if text in self.nlp_cache:
            doc = self.nlp_cache.get(text)
        else:
            doc = nlp(text)
            self.nlp_cache[text] = doc

        for tok in doc:
            toks.append(
                ParsedToken(tok.text, not tok.is_punct, tok.is_sent_end, tok.lemma_)
            )
            if tok.whitespace_ != "":
                toks.append(ParsedToken(tok.whitespace_, False))
        if len(text) > 3:
            self._set_cache(f"{i}-{text}", toks)
        return toks


class TurkishParser(SpaceDelimitedParser):
    "Parser to handle Turkish parsing fun."

    @classmethod
    def name(cls):
        return "Turkish"

    def get_lowercase(self, text):
        "Handle the funny turkish i variants."
        for caps, lower in {"İ": "i", "I": "ı"}.items():
            text = text.replace(caps, lower)
        return text.lower()
