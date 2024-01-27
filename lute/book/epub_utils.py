import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup


def clean_filename(filename):
    replace_str = "@-"
    for c in replace_str:
        filename = filename.replace(c, "")
    return filename.lstrip("./")


def get_img_name(img):
    src = img.attrs["src"]
    return clean_filename(os.path.basename(src))


def get_images(book):
    is_success = False
    res = []
    try:
        for img in book.get_items_of_type(ebooklib.ITEM_IMAGE):
            file_base_name = clean_filename(os.path.basename(img.file_name))
            res.append((file_base_name, img.content))
        is_success = True
    except Exception as e:
        print(str(e))

    return res


def parse_document(soup):
    docs = []
    for child in soup.findAll():
        if child.name in ("p", "img", "h2"):
            if child.name in ("p", "h2"):
                # display(HTML(f'<p>{child.text[:10]}</p>'))
                docs.append(child.text)
            elif child.name == "img":
                # display(Image(img_dict[get_img_name(child)]))
                img_name = get_img_name(child)
                docs.append(f"<img={img_name}")
    return docs


def parse_epub(book):
    res = []
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        html = item.get_body_content().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        # body = soup.find("body")

        if soup:
            res.extend(parse_document(soup))
        else:
            print("Error", item.get_name())
    return "\n".join(res)
