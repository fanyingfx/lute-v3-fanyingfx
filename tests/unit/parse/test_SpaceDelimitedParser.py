"""
SpaceDelimitedParser tests.
"""

from lute.parse.space_delimited_parser import SpaceDelimitedParser
from lute.parse.base import ParsedToken


def assert_tokens_equals(text, lang, expected):
    """
    Parsing a text using a language should give the expected parsed tokens.

    expected is given as array of:
    [ original_text, is_word, is_end_of_sentence ]
    """
    p = SpaceDelimitedParser()
    actual = p.get_parsed_tokens(text, lang)
    expected = [ParsedToken(*a) for a in expected]
    assert [str(a) for a in actual] == [str(e) for e in expected]


def assert_string_equals(text, lang, expected):
    """
    Parsing a text with a language's settings should yield tokens.

    Similar to assert_tokens_equals, but it stringizes the tokens, e.g.:
    'Hi.\nGoodbye.' => '[Hi].¶[Goodbye].'
    """
    p = SpaceDelimitedParser()
    actual = p.get_parsed_tokens(text, lang)

    def to_string(tokens):
        ret = ""
        for tok in tokens:
            s = tok.token
            if tok.is_word:
                s = "[" + s + "]"
            ret += s
        return ret

    assert to_string(actual) == expected


def test_end_of_sentence_stored_in_parsed_tokens(spanish):
    "ParsedToken is marked as EOS=True at ends of sentences."
    s = "Tengo un gato.\nTengo dos."

    expected = [
        ("Tengo", True, False, "tengo"),
        (" ", False, False, None),
        ("un", True, False, "un"),
        (" ", False, False, None),
        ("gato", True, False, "gato"),
        (".", False, True, None),
        ("¶", False, True, None),
        ("Tengo", True, False, "tengo"),
        (" ", False, False, None),
        ("dos", True, False, "do"),
        (".", False, True, None),
    ]

    assert_tokens_equals(s, spanish, expected)


def test_exceptions_are_considered_when_splitting_sentences(english):
    "Languages can have exceptions (like 'Mrs.') that shouldn't split sentences."
    s = "1. Mrs. Jones is here."

    expected = [
        ("1. ", False, True, None),
        ("Mrs.", True, False, "mrs."),
        (" ", False, False, None),
        ("Jones", True, False, "jones"),
        (" ", False, False, None),
        ("is", True, False, "be"),
        (" ", False, False, None),
        ("here", True, False, "here"),
        (".", False, True, None),
    ]

    assert_tokens_equals(s, english, expected)


def test_single_que(spanish):
    """
    Sanity check: que with accent was getting mishandled.
    """
    text = "Tengo que y qué."
    expected = [
        ("Tengo", True, False, "tengo"),
        (" ", False, False, None),
        ("que", True, False, "que"),
        (" ", False, False, None),
        ("y", True, False, "y"),
        (" ", False, False, None),
        ("qué", True, False, "qué"),
        (".", False, True, None),
    ]
    assert_tokens_equals(text, spanish, expected)


def test_EE_UU_exception_should_be_considered(spanish):
    """
    An exception containing multiple dots should be one single token.
    """
    s = "Estamos en EE.UU. hola."
    spanish.exceptions_split_sentences = "EE.UU."

    expected = [
        ("Estamos", True, False, "estamos"),
        (" ", False, False, None),
        ("en", True, False, "en"),
        (" ", False, False, None),
        ("EE.UU.", True, False, "ee.uu."),
        (" ", False, False, None),
        ("hola", True, False, "hola"),
        (".", False, True, None),
    ]

    assert_tokens_equals(s, spanish, expected)


def test_just_EE_UU(spanish):
    """
    A sentence of a single word, where that word is an exception, should be a single token.
    """
    s = "EE.UU."
    spanish.exceptions_split_sentences = "EE.UU."
    expected = [
        ("EE.UU.", True, False, "ee.uu."),
    ]
    assert_tokens_equals(s, spanish, expected)


def test_quick_checks(english):
    "Fast sanity checks."
    assert_string_equals("test", english, "[test]")
    assert_string_equals("test.", english, "[test].")
    assert_string_equals('"test."', english, '"[test]."')
    assert_string_equals('"test".', english, '"[test]".')
    assert_string_equals("Hi there.", english, "[Hi] [there].")
    assert_string_equals("Hi there.  Goodbye.", english, "[Hi] [there]. [Goodbye].")
    assert_string_equals("Hi.\nGoodbye.", english, "[Hi].¶[Goodbye].")
    assert_string_equals("He123llo.", english, "[He]123[llo].")
    assert_string_equals("1234", english, "1234")
    assert_string_equals("1234.", english, "1234.")
    assert_string_equals("1234.Hello", english, "1234.[Hello]")
