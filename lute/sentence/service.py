from lute import db
from lute.models.sentence_note import SentenceNote
from lute.models.book import Book


def get_all_sentencenotes(db_session):
    snotes = db_session.query(SentenceNote).all()
    res = []
    for snote in snotes:
        # d = dict(
        #     bookname=Book.find(snote.book_id).title,
        #     sentence=snote.sentence,
        #     tags=",".join(snote.sentence_tags),
        #     sentencenote=snote.sentence_note,
        #     sentencenoteid=snote.id,
        # )
        l = [
            snote.sentence,
            snote.sentence_note,
            ",".join(snote.sentence_tags),
            Book.find(snote.book_id).title,
            snote.id,
        ]
        res.append(l)
    return {"data": res}
