"""
/read endpoints.
"""

from datetime import datetime
from flask import Blueprint, flash, request, render_template, redirect, jsonify

from lute.models.sentence_note import SentenceNote
from lute.read.service import (
    set_unknowns_to_known,
    # parse_paragraphs,
    start_reading,
    get_sentencenote,
    create_or_update_sentence_note,
    delete_sentence_note,
)
from lute.read.forms import TextForm
from lute.term.model import Repository
from lute.term.routes import handle_term_form
from lute.models.book import Book, Text
from lute.models.term import Term as DBTerm, TermTag
from lute.models.setting import UserSetting
from lute.db import db

bp = Blueprint("read", __name__, url_prefix="/read")


def _render_book_page(book, pagenum):
    """
    Render a particular book page.
    """
    lang = book.language
    show_highlights = bool(int(UserSetting.get_value("show_highlights")))

    return render_template(
        "read/index.html",
        hide_top_menu=True,
        is_rtl=lang.right_to_left,
        html_title=book.title,
        book=book,
        dictionary_url=lang.sentence_translate_uri,
        page_num=pagenum,
        page_count=book.page_count,
        show_highlights=show_highlights,
    )


@bp.route("/<int:bookid>", methods=["GET"])
def read(bookid):
    """
    Read a book, opening to its current page.

    This is called from the book listing, on Lute index.
    """
    book = Book.find(bookid)
    if book is None:
        flash(f"No book matching id {bookid}")
        return redirect("/", 302)

    page_num = 1
    text = book.texts[0]
    if book.current_tx_id:
        text = Text.find(book.current_tx_id)
        page_num = text.order

    return _render_book_page(book, page_num)


@bp.route("/<int:bookid>/page/<int:pagenum>", methods=["GET"])
def read_page(bookid, pagenum):
    """
    Read a particular page of a book.

    Called from term Sentences link.
    """
    book = Book.find(bookid)
    if book is None:
        flash(f"No book matching id {bookid}")
        return redirect("/", 302)

    pagenum = book.page_in_range(pagenum)
    return _render_book_page(book, pagenum)


@bp.route("/page_done", methods=["post"])
def page_done():
    "Handle POST when page is done."
    data = request.json
    bookid = int(data.get("bookid"))
    pagenum = int(data.get("pagenum"))
    restknown = data.get("restknown")

    book = Book.find(bookid)
    text = book.text_at_page(pagenum)
    text.read_date = datetime.now()
    db.session.add(text)
    db.session.commit()
    if restknown:
        set_unknowns_to_known(text)
    return jsonify("ok")


@bp.route("/save_player_data", methods=["post"])
def save_player_data():
    "Save current player position, bookmarks.  Called on a loop by the player."
    data = request.json
    bookid = int(data.get("bookid"))
    book = Book.find(bookid)
    book.audio_current_pos = float(data.get("position"))
    book.audio_bookmarks = data.get("bookmarks")
    db.session.add(book)
    db.session.commit()
    return jsonify("ok")


# @bp.route("/preloadpage/<int:bookid>/<int:pagenum>", methods=["GET"])
# def preload_page(bookid, pagenum):
#     "Method called by ajax, just for cache"
#     book = Book.find(bookid)
#     if book is None:
#         flash(f"No book matching id {bookid}")
#         return ""
#
#     pagenum = _page_in_range(book, pagenum)
#     # for cache
#     # page_num_next = _page_in_range(book, pagenum + 1)
#     # get_paragraphs(book.texts[page_num_next])
#     text = book.texts[pagenum - 1]
#     paragraphs = get_paragraphs(text)
#     return ""
#


@bp.route("/renderpage/<int:bookid>/<int:pagenum>", methods=["GET"])
def render_page(bookid, pagenum):
    "Method called by ajax, render the given page."
    book = Book.find(bookid)
    if book is None:
        flash(f"No book matching id {bookid}")
        return redirect("/", 302)
    paragraphs = start_reading(book, pagenum, db.session)
    return render_template("read/page_content.html", paragraphs=paragraphs)


@bp.route("/empty", methods=["GET"])
def empty():
    "Show an empty/blank page."
    return ""


@bp.route("/termform/<int:langid>/<text>", methods=["GET", "POST"])
def term_form(langid, text):
    """
    Create or edit a term.
    """
    lemma = request.args.get("lemma", default=None, type=str)
    if not lemma == "None":
        lemma = lemma.replace(",", "")
    else:
        lemma = text

    reading = request.args.get("reading", default=None, type=str) or request.form.get(
        "romanization", ""
    )
    # TODO find a better way to handle reading for multi-term
    if reading.replace("None", "").replace("・", "").strip() == "":
        reading = ""
    tokens_raw = request.args.get("textparts", None)
    # if '\u200b' in text:
    #     raw_tokens_in_text = text.split('\u200b')
    if tokens_raw:
        raw_tokens = tokens_raw.split(",")
    elif "\u200b" in text:
        raw_tokens = text.split("\u200b")
    else:
        raw_tokens = None

    # raw_tokens = tokens_raw.split(",") if tokens_raw else None

    repo = Repository(db)
    term = repo.find_or_new(langid, text, lemma, reading, raw_tokens)

    return handle_term_form(
        term,
        repo,
        "/read/frameform.html",
        render_template("/read/updated.html", term_text=term.text),
        embedded_in_reading_frame=True,
        tokens_raw=tokens_raw,
    )


@bp.route("/termpopup/<int:termid>", methods=["GET"])
def term_popup(termid):
    """
    Show a term popup for the given DBTerm.
    """
    term = DBTerm.query.get(termid)

    term_tags = [tt.text for tt in term.term_tags]

    def make_array(t):
        ret = {
            "term": t.text,
            "roman": t.romanization,
            "trans": t.translation if t.translation else "-",
            "tags": [tt.text for tt in t.term_tags],
        }
        return ret

    parent_terms = [p.text for p in term.parents]
    parent_terms = ", ".join(parent_terms)

    parent_data = []
    if len(term.parents) == 1:
        parent = term.parents[0]
        if parent.translation != term.translation:
            parent_data.append(make_array(parent))
    else:
        parent_data = [make_array(p) for p in term.parents]

    images = [term.get_current_image()] if term.get_current_image() else []
    for p in term.parents:
        if p.get_current_image():
            images.append(p.get_current_image())

    images = list(set(images))

    return render_template(
        "read/termpopup.html",
        term=term,
        flashmsg=term.get_flash_message(),
        term_tags=term_tags,
        term_images=images,
        parentdata=parent_data,
        parentterms=parent_terms,
    )


@bp.route("/flashcopied", methods=["GET"])
def flashcopied():
    return render_template("read/flashcopied.html")


# @bp.post("/parse_text")
# def parse_text():
#     data=request.json
#     if 'text' not in data or 'language' not in data:
#         return jsonify({"error": ""})
#     text = data['text']
#     language = data['language']
#     lang=Language.find_by_name(language)
#     paras= parse_paragraphs(text,lang)
#     return jsonify(paras)


@bp.route("/editpage/<int:bookid>/<int:pagenum>", methods=["GET", "POST"])
def edit_page(bookid, pagenum):
    "Edit the text on a page."
    book = Book.find(bookid)
    text = book.text_at_page(pagenum)
    if text is None:
        return redirect("/", 302)
    form = TextForm(obj=text)

    if form.validate_on_submit():
        form.populate_obj(text)
        db.session.add(text)
        db.session.commit()
        return redirect(f"/read/{book.id}", 302)

    return render_template("read/page_edit_form.html", hide_top_menu=True, form=form)


@bp.route("/editsentence/<int:bookid>/<int:pagenum>", methods=["GET", "POST"])
def edit_sentence(bookid, pagenum):
    book = Book.find(bookid)
    sentence = request.args.get("sentence")
    if sentence is None or sentence.strip() == "":
        return redirect("/", 302)
    text = book.text_at_page(pagenum)
    raw_text = text.text
    # raw_sentence = sentence.replace('\u200b', '')
    raw_sentence = sentence
    text.text = sentence
    form = TextForm(obj=text)
    if form.validate_on_submit():
        new_senetence = form.text.data
        new_text = raw_text.replace(raw_sentence, new_senetence)
        form.populate_obj(text)
        text.text = new_text
        note: SentenceNote = get_sentencenote(bookid, pagenum, sentence, db.session)
        db.session.add(text)
        if note is not None:
            note.sentence = new_senetence
            db.session.add(note)
        db.session.commit()
        return redirect(f"/read/{book.id}", 302)

    return render_template("read/page_edit_form.html", hide_top_menu=True, form=form)


@bp.get("/sentencenote/<bookid>/<pagenum>/<sentence>")
def sentencenote(bookid, pagenum, sentence):
    note: SentenceNote = get_sentencenote(bookid, pagenum, sentence, db.session)
    if note is None:
        return jsonify(dict(sentence_note=""))

    data = dict(
        sentence_note=note.sentence_note,
        tags=[{"value": t.text} for t in note.sentence_tags],
    )
    return jsonify(data)


@bp.post("/sentencenote/<bookid>/<pagenum>/<sentence>")
def update_sentencenote(bookid, pagenum, sentence):
    new_note = request.json.get("new_note", "")
    raw_tags = request.json.get("tags", [])
    tags = [tag["value"] for tag in raw_tags]
    # try:
    if new_note.strip() != "":
        create_or_update_sentence_note(
            bookid, pagenum, sentence, new_note, tags, db.session
        )
        res = {"status": "1", "message": "Update note successful"}
    else:
        if delete_sentence_note(bookid, pagenum, sentence, db.session):
            res = {"status": "2", "message": "Note deleted!"}
        else:
            res = {"status": "1", "message": "Note is empty!"}

    # except:
    #     res = {"status": "0", "message": "Update note failed"}

    return jsonify(res)
