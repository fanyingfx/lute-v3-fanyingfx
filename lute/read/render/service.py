"""
Reading rendering helpers.
"""

import re
from typing import List, Tuple, Set, FrozenSet, Dict

from sqlalchemy import text as sqltext

from lute.models.sentence_note import SentenceNote
from lute.models.setting import UserSetting
from lute.models.term import Term
from lute.parse.base import ParsedToken
from lute.read.render.renderable_calculator import RenderableCalculator
from lute.db import db


def clean_text(text):
    zws = "\u200b"
    text = text.strip()
    chars_should_be_cleaned = [zws, "「", "」"]
    for c in chars_should_be_cleaned:
        text = text.replace(c, "")
    return text


def find_all_Terms_in_string(s, language):  # pylint: disable=too-many-locals
    """
    Find all terms contained in the string s.

    For example
    - given s = "Here is a cat"
    - given terms in the db: [ "cat", "a cat", "dog" ]

    This would return the terms "cat" and "a cat".

    The code first queries for exact single-token matches,
    and then multiword matches, because that's much faster
    than querying for everthing at once.  (This may no longer
    be true, can change it later.)
    """

    # Extract word tokens from the input string
    cleaned = re.sub(r"\s+", " ", s)
    tokens = language.get_parsed_tokens(cleaned)

    parser = language.parser

    # fyi - Manually searching for terms was slow (i.e., querying for
    # all terms, and checking if the strings were in the string s).

    # Query for terms with a single token that match the unique word tokens
    word_tokens = filter(lambda t: t.is_word, tokens)
    tok_strings = [parser.get_lowercase(t.token) for t in word_tokens]
    tok_strings = list(set(tok_strings))
    terms_matching_tokens = (
        db.session.query(Term)
        .filter(
            Term.language == language,
            Term.text_lc.in_(tok_strings),
            Term.token_count == 1,
        )
        .all()
    )

    # Multiword terms have zws between all tokens.
    # Create content string with zws between all tokens for the match.
    zws = "\u200B"  # zero-width space
    lctokens = [parser.get_lowercase(t.token) for t in tokens]
    content = zws + zws.join(lctokens) + zws

    sql = sqltext(
        """
        SELECT WoID FROM words
        WHERE WoLgID=:language_id and WoTokenCount>1
        AND :content LIKE '%' || WoTextLC || '%'
        """
    )
    sql = sql.bindparams(language_id=language.id, content=content)
    idlist = db.session.execute(sql).all()
    woids = [int(p[0]) for p in idlist]
    contained_terms = db.session.query(Term).filter(Term.id.in_(woids)).all()

    # Note that the above method (querying for ids, then getting terms)
    # is faster than using the model as shown below!
    ### contained_term_query = db.session.query(Term).filter(
    ###     Term.language == language,
    ###     Term.token_count > 1,
    ###     func.instr(content, Term.text_lc) > 0,
    ### )
    ### contained_terms = contained_term_query.all()

    return terms_matching_tokens + contained_terms


def find_all_sentences_with_note(bookid, page_num) -> Dict[str, bool]:
    sentences_with_note: List[SentenceNote] = (
        db.session.query(SentenceNote)
        .filter(SentenceNote.book_id == bookid, SentenceNote.page_id == page_num)
        .all()
    )
    return {sn.sentence: "?" in sn.get_sentence_tags() for sn in sentences_with_note}


class RenderableSentence:
    """
    A collection of TextItems to be rendered.
    """

    def __init__(self, sentence_id, textitems):
        self.sentence_id = sentence_id
        self.textitems = textitems
        self.sentence_with_note = False
        self.sentence_note_has_question = False

    def __repr__(self):
        s = "".join([t.display_text for t in self.textitems])
        return f'<RendSent {self.sentence_id}, {len(self.textitems)} items, "{s}">'

    def get_sentence(self):
        return "".join([clean_text(t.display_text) for t in self.textitems])


# @lru_cache()
def get_paragraphs(s, language, bookid=0, page_num=1):
    """
    Get array of arrays of RenderableSentences for the given string s.
    """

    # Hacky reset of state of ParsedToken state.
    # _Shouldn't_ matter ... :-(
    ParsedToken.reset_counters()
    tokens = language.get_parsed_tokens(s)
    tokens = [t for t in tokens if t.token != "¶"]

    # Brutal hack ... the RenderableCalculator requires the
    # ParsedTokens to be in contiguous order, but the above list
    # comprehension can cause some tokens to get removed.  In addition
    # (and this is the worst part), for some reason the tests fail in
    # CI, but _inconsistently_, with the token order numbers.  The
    # order sometimes jumps by 2 ... I really can't explain it.  So,
    # as a _complete hack_, I'm re-numbering the tokens now, to ensure
    # they're in order.
    tokens.sort(key=lambda x: x.order)
    if len(tokens) > 0:
        n = tokens[0].order
        for t in tokens:
            t.order = n
            n += 1
    terms = find_all_Terms_in_string(s, language)
    if UserSetting.key_exists("show_reading") and language.show_romanization:
        show_reading = bool(int(UserSetting.get_value("show_reading")))
    else:
        show_reading = False
    sentences_with_note = find_all_sentences_with_note(bookid, page_num)

    def make_RenderableSentence(pnum, sentence_num, tokens, terms):
        """
        Make a RenderableSentences using the tokens present in
        that sentence.  The current text and language are pulled
        into the function from the closure.
        """
        nonlocal sentences_with_note
        sentence_tokens = [t for t in tokens if t.sentence_number == sentence_num]
        renderable = RenderableCalculator.get_renderable(
            language, terms, sentence_tokens
        )
        textitems = [
            i.make_text_item(pnum, sentence_num, language, show_reading, bookid)
            for i in renderable
        ]
        ret = RenderableSentence(sentence_num, textitems)
        if ret.get_sentence() in sentences_with_note:
            ret.sentence_with_note = True
            ret.sentence_note_has_question = sentences_with_note[ret.get_sentence()]
        return ret

    def unique(arr):
        return list(set(arr))

    renderable_paragraphs = []
    paranums = sorted(unique([t.paragraph_number for t in tokens]))
    for pnum in paranums:
        paratokens = [t for t in tokens if t.paragraph_number == pnum]
        senums = sorted(unique([t.sentence_number for t in paratokens]))

        # A renderable paragraph is a collection of
        # RenderableSentences.
        renderable_sentences = [
            make_RenderableSentence(pnum, senum, paratokens, terms) for senum in senums
        ]
        renderable_paragraphs.append(renderable_sentences)

    return renderable_paragraphs
