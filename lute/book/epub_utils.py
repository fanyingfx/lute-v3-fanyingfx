import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup


def get_img_name(img):
    src = img.attrs["src"]
    return os.path.basename(src)


def get_images(book):
    is_success = False
    res = []
    try:
        for img in book.get_items_of_type(ebooklib.ITEM_IMAGE):
            file_base_name = os.path.basename(img.file_name)
            res.append((file_base_name, img.content))
            # img_path = os.path.join(img_dir, file_base_name)
            # # with open(img_path, "wb") as f:
            #     f.write(img.content)
        is_success = True
    except:
        pass
    return res


def parse_document(body):
    docs = []
    for child in body.findAll():
        if child.name in ("p", "img"):
            if child.name == "p":
                # display(HTML(f'<p>{child.text[:10]}</p>'))
                docs.append(child.text)
            elif child.name == "img":
                # display(Image(img_dict[get_img_name(child)]))
                docs.append(f"<img={get_img_name(child)}")
    return docs


def parse_epub(book):
    res = []
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        html = item.get_body_content().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        body = soup.find("body")

        if body:
            res.extend(parse_document(body))
        else:
            print("Error", item.get_name())
    return "\n".join(res)
