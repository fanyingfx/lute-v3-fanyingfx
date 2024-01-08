"""
User images routes.

User images are stored in the database as /userimages/langid/term, but
with no jpeg extension.  Reason: the old symfony code couldn't manage
urls with periods.
"""

import os
from flask import Blueprint, send_from_directory, current_app

bp = Blueprint("bookimages", __name__, url_prefix="/bookimages")


@bp.route("/<int:bookid>/<img_name>", methods=["GET"])
def get_image(bookid, img_name):
    "Serve the image from the data/bookimages directory."
    datapath = current_app.config["DATAPATH"]
    directory = os.path.join(datapath, "bookimages", str(bookid))
    filename = img_name
    print(directory, img_name)
    return send_from_directory(directory, filename)
