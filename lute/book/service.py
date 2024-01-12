"""
book helper routines.
"""

import os
import tempfile
from datetime import datetime

# pylint: disable=unused-import
from tempfile import TemporaryFile, SpooledTemporaryFile
import requests
from flask import current_app, flash
from openepub import Epub, EpubError
from pypdf import PdfReader
from werkzeug.utils import secure_filename

from lute.book import epub_utils
from lute.book.model import Book
from ebooklib import epub
from bs4 import BeautifulSoup
import shutil


class BookImportException(Exception):
    """
    Exception to throw on book import error.
    """

    def __init__(self, message="A custom error occurred", cause=None):
        self.cause = cause
        self.message = message
        super().__init__(message)


def _secure_unique_fname(filename):
    """
    Return secure name pre-pended with datetime string.
    """
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y%m%d_%H%M%S")
    f = "_".join([formatted_datetime, secure_filename(filename)])
    return f


def save_audio_file(audio_file_field_data):
    """
    Save the file to disk, return its filename.
    """
    filename = _secure_unique_fname(audio_file_field_data.filename)
    fp = os.path.join(current_app.env_config.useraudiopath, filename)
    audio_file_field_data.save(fp)
    return filename


def get_textfile_content(filefielddata):
    "Get content as a single string."
    content = ""
    try:
        content = filefielddata.read()
        return str(content, "utf-8")
    except UnicodeDecodeError as e:
        f = filefielddata.filename
        msg = f"{f} is not utf-8 encoding, please convert it to utf-8 first (error: {str(e)})"
        raise BookImportException(message=msg, cause=e) from e


def get_epub_content(epub_file_field_data):
    """
    Get the content of the epub as a single string.
    """
    content = ""
    try:
        if hasattr(epub_file_field_data.stream, "seekable"):
            epub = Epub(stream=epub_file_field_data.stream)
            content = epub.get_text()
        else:
            # We get a SpooledTemporaryFile from the form but this doesn't
            # implement all file-like methods until python 3.11. So we need
            # to rewrite it into a TemporaryFile
            with TemporaryFile() as tf:
                epub_file_field_data.stream.seek(0)
                tf.write(epub_file_field_data.stream.read())
                epub = Epub(stream=tf)
                content = epub.get_text()
    except EpubError as e:
        msg = f"Could not parse {epub_file_field_data.filename} (error: {str(e)})"
        raise BookImportException(message=msg, cause=e) from e
    return content


def get_pdf_content_from_form(pdf_file_field_data):
    "Get content as a single string from a PDF file using PyPDF2."
    content = ""
    try:
        pdf_reader = PdfReader(pdf_file_field_data)

        for page in pdf_reader.pages:
            content += page.extract_text()

        return content
    except Exception as e:
        msg = f"Could not parse {pdf_file_field_data.filename} (error: {str(e)})"
        raise BookImportException(message=msg, cause=e) from e


def get_epub_content_new(epub_file):
    content = ""
    with tempfile.NamedTemporaryFile() as fp:
        epub_file.stream.seek(0)
        fp.write(epub_file.stream.read())
        book = epub.read_epub(fp.name)
    img_data = epub_utils.get_images(book)

    book_data = epub_utils.parse_epub(book)
    return book_data, img_data


def save_image(filename, content, bookid):
    img_dir = os.path.join(current_app.env_config.bookimagespath, str(bookid))
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    fp = os.path.join(img_dir, filename)
    with open(fp, "wb") as f:
        f.write(content)


def delete_book_image(bookid):
    img_dir = os.path.join(current_app.env_config.bookimagespath, str(bookid))
    if os.path.exists(img_dir):
        try:
            shutil.rmtree(img_dir)
        except:
            pass


def book_from_url(url):
    "Parse the url and load a new Book."
    s = None
    try:
        timeout = 20  # seconds
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        s = response.text
    except requests.exceptions.RequestException as e:
        msg = f"Could not parse {url} (error: {str(e)})"
        raise BookImportException(message=msg, cause=e) from e

    soup = BeautifulSoup(s, "html.parser")
    extracted_text = []

    # Add elements in order found.
    for element in soup.descendants:
        if element.name in ("h1", "h2", "h3", "h4", "p"):
            extracted_text.append(element.text)

    title_node = soup.find("title")
    orig_title = title_node.string if title_node else url

    short_title = orig_title[:150]
    if len(orig_title) > 150:
        short_title += " ..."

    b = Book()
    b.title = short_title
    b.source_uri = url
    b.text = "\n\n".join(extracted_text)
    return b
