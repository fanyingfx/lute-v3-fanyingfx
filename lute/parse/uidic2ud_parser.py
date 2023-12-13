from typing import List

import unidic2ud
from base import AbstractParser


class Unidic2udParser(AbstractParser):
    @classmethod
    def name(cls):
        return "Unidic2udParser"

    def get_parsed_tokens(self, text: str, language) -> List:
        pass
