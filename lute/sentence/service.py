from lute import db
from lute.models.sentence_note import SentenceNote
from lute.models.book import Book
from sqlalchemy.orm.session import Session


def get_all_sentencenotes(db_session: Session):
    snotes = (
        db_session.query(SentenceNote).order_by(SentenceNote.sn_updated.desc()).all()
    )
    res = []
    # dict(
    #     sentence=snote.sentence,
    #     sentence_note=snote.sentence_note,
    #     sentence_tags="|".join((t.text for t in snote.sentence_tags)),
    #     book_title=Book.find(snote.book_id).title,
    #     book_id=snote.book_id,
    #     page_num=snote.page_id,
    # )
    for snote in snotes:
        res.append(
            [
                snote.sentence,
                snote.sentence_note,
                f"/read/{snote.book_id}/page/{snote.page_id}",
                "|".join((t.text for t in snote.sentence_tags)),
                Book.find(snote.book_id).title,
            ]
        )
    return {"data": res}
