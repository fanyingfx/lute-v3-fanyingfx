"""
Parser registry.

List of available parsers.
"""

from lute.models.setting import UserSetting

from lute.parse.base import AbstractParser
from lute.parse.space_delimited_parser import SpaceDelimitedParser, TurkishParser
from lute.parse.fugashi_parser import FugashiParser
from lute.parse.character_parser import ClassicalChineseParser
from lute.parse.mandarin_parser import MandarinParser
from lute.parse.english_parser import EnglishParser

# List of ALL parsers available, not necessarily all supported.
# This design feels fishy, but it suffices for now.
parsers = {
    "spacedel": SpaceDelimitedParser,
    "english": EnglishParser,
    "turkish": TurkishParser,
    "japanese": FugashiParser,
    "classicalchinese": ClassicalChineseParser,
    "mandarin": MandarinParser,
}
parser_instances = {}


def _init_jp_parser(name):
    parser_instances["japanese"] = parsers["japanese"]()
    if UserSetting.key_exists("unidic_types"):
        unidic_type = UserSetting.get_value("unidic_types")
        parser_instances["japanese"].switch_tagger(unidic_type)


def _supported_parsers():
    "Get the supported parsers."
    ret = {}
    for k, v in parsers.items():
        if v.is_supported():
            ret[k] = v
    return ret


def get_parser(parser_name) -> AbstractParser:
    "Return the supported parser with the given name."
    if parser_name in _supported_parsers():
        if parser_name in parser_instances:
            return parser_instances[parser_name]
        if parser_name == "japanese":
            _init_jp_parser(parser_name)
        else:
            pclass = parsers[parser_name]
            parser_instances[parser_name] = pclass()
        return parser_instances[parser_name]

    raise ValueError(f"Unknown parser type '{parser_name}'")


def is_supported(parser_name) -> bool:
    "Return True if the specified parser is supported, false otherwise or if not found."
    if parser_name not in parsers:
        return False
    p = parsers[parser_name]
    return p.is_supported()


def supported_parsers():
    """
    Dictionary of supported parser strings and class names, for UI.

    For select list entries, use supported_parsers().items().
    """
    ret = []
    for k, v in _supported_parsers().items():
        ret.append([k, v.name()])
    return ret


def supported_parser_types():
    """
    List of supported Language.parser_types
    """
    return list(_supported_parsers().keys())
