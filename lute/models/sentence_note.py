from lute.db import db

sentencenotestags = db.Table(
    "sentencenotetags",
    db.Model.metadata,
    db.Column("SeNtTgID", db.Integer, db.ForeignKey("tags.TgID")),
    db.Column("SeNtID", db.Integer, db.ForeignKey("sentencenote.SeNtID")),
)


class SentenceNote(db.Model):
    __tablename__ = "sentencenote"

    id = db.Column("SeNtID", db.SmallInteger, primary_key=True)
    book_id = db.Column("BookID", db.Integer)
    page_id = db.Column("PageID", db.Integer)

    sentence = db.Column("SeText", db.String(500))
    sn_updated = db.Column(
        "SnUpdated", db.DateTime, default=db.func.current_timestamp()
    )

    sentence_note = db.Column("SeNtText", db.Text())
    sentence_tags = db.relationship("TermTag", secondary="sentencenotetags")

    def __init__(self, bookid, pagenum, sentence, sentence_note):
        self.book_id = bookid
        self.page_id = pagenum
        self.sentence = sentence
        self.sentence_note = sentence_note
        self.term_tags = []

    def get_sentence_tags(self):
        return [tag.text for tag in self.sentence_tags]

    @staticmethod
    def find(sentence):
        return (
            db.session.query(SentenceNote)
            .filter(SentenceNote.sentence == sentence)
            .first()
        )

    def remove_all_snote_tags(self):
        self.sentence_tags = []

    def add_snote_tag(self, snote_tag):
        if snote_tag not in self.sentence_tags:
            self.sentence_tags.append(snote_tag)

    def remove_snote_tag(self, snote_tag):
        self.sentence_tags.remove(snote_tag)


# class SentenceTag(db.Model):
#     "Term tags."
#     __tablename__ = "sentencetags"
#
#     id = db.Column("TgID", db.Integer, primary_key=True)
#     text = db.Column("TgText", db.String(20))
#     _comment = db.Column("TgComment", db.String(200))


if __name__ == "__main__":
    from sqlalchemy import create_engine

    engine = create_engine(
        "sqlite:////home/fan/.local/share/test_lute/test_lute13.db", echo=True
    )
    m = db.metadata
    m.create_all(bind=engine)

    # print(wordtags.schema)
