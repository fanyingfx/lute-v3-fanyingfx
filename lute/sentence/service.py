from lute import db
from lute.models.sentence_note import SentenceNote
from lute.models.book import Book
from sqlalchemy.orm.session import Session


def get_all_sentencenotes(db_session: Session):
    snotes = (
        db_session.query(SentenceNote).order_by(SentenceNote.sn_updated.desc()).all()
    )
    res = []
    for snote in snotes:
        l = [
            snote.sentence,
            snote.sentence_note,
            "|".join((t.text for t in snote.sentence_tags)),
            Book.find(snote.book_id).title,
            snote.id,
        ]
        res.append(l)
    return {"data": res}
