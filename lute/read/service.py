"""
Reading helpers.
"""
from sqlalchemy.orm import Session

from lute.models.sentence_note import SentenceNote
from lute.models.term import Term, Status, TermTag
from lute.models.book import Text
from lute.book.stats import mark_stale
from lute.read.render.service import get_paragraphs
from lute.term.model import Repository

from lute.db import db


def set_unknowns_to_known(text: Text):
    """
    Given a text, create new Terms with status Well-Known
    for any new Terms.
    """
    language = text.book.language

    sentences = sum(get_paragraphs(text.text, text.book.language), [])

    tis = []
    for sentence in sentences:
        for ti in sentence.textitems:
            tis.append(ti)

    def is_unknown(ti):
        return (
                ti.is_word == 1
                and (ti.wo_id == 0 or ti.wo_id is None)
                and ti.token_count == 1
        )

    unknowns = list(filter(is_unknown, tis))
    words_lc = [ti.text_lc for ti in unknowns]
    uniques = list(set(words_lc))
    uniques.sort()

    batch_size = 100
    i = 0

    # There is likely a better way to write this using generators and
    # yield.
    for u in uniques:
        candidate = Term(language, u)
        t = Term.find_by_spec(candidate)
        if t is None:
            candidate.status = Status.WELLKNOWN
            db.session.add(candidate)
            i += 1

        if i % batch_size == 0:
            db.session.commit()

    # Commit any remaining.
    db.session.commit()


def bulk_status_update(text: Text, terms_text_array, new_status):
    """
    Given a text and list of terms, update or create new terms
    and set the status.
    """
    language = text.book.language
    repo = Repository(db)
    for term_text in terms_text_array:
        t = repo.find_or_new(language.id, term_text)
        t.status = new_status
        repo.add(t)
    repo.commit()


def start_reading(dbbook, pagenum, db_session):
    "Start reading a page in the book, getting paragraphs."

    text = dbbook.text_at_page(pagenum)
    text.load_sentences()

    mark_stale(dbbook)
    dbbook.current_tx_id = text.id
    db_session.add(dbbook)
    db_session.add(text)
    db_session.commit()

    paragraphs = get_paragraphs(text.text, text.book.language, text.bk_id)

    return paragraphs


def get_sentencenote(bookid, pagenum, sentence, db_session: Session):
    return (
        db_session.query(SentenceNote)
        .filter_by(book_id=bookid, page_id=pagenum, sentence=sentence)
        .first()
    )


def create_or_update_sentence_note(
        bookid, pagenum, sentence, text_note, tags, db_session: Session
):
    note = (
        db_session.query(SentenceNote)
        .filter_by(book_id=bookid, page_id=pagenum, sentence=sentence)
        .first()
    )
    sentence_tags = []
    if note is None:
        note = SentenceNote(bookid, pagenum, sentence, text_note)
    else:
        note.sentence_note = text_note
    for s in tags:
        sentence_tags.append(TermTag.find_or_create_by_text(s))
    note.remove_all_snote_tags()
    for st in sentence_tags:
        note.add_snote_tag(st)
    db_session.add(note)
    db_session.commit()
