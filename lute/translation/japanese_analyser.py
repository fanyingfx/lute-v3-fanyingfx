import re

import requests
from bs4 import BeautifulSoup

URL = "https://jastudy.net/"


def get_spinfo(sp_list):
    reg = re.compile("【接続】：(.*)【意味】：(.*)【例文】.*")
    title = sp_list.find(id="title")
    level = sp_list.find(class_="now_level")
    info = sp_list.find(id="sp_infomation")
    rr = reg.match(info.text.replace("\xa0", " "))
    if rr:
        form = rr.group(1)
        meaning = rr.group(2)
    else:
        form = ""
        meaning = ""
    return f"{title.text}{level.text}\n{form}{meaning}"


def get_analyzed_res(text):
    form_data = {"JapneseText": text}
    r = requests.post(URL, data=form_data)
    soup = BeautifulSoup(r.text, "html.parser")
    vocab_list = soup.find(id="vocab_show")
    sp_lists = vocab_list.find_all(id="sp_list")
    res_l = [get_spinfo(sp_list) for sp_list in sp_lists]
    return "\n".join(res_l)


if __name__ == "__main__":
    print(get_analyzed_res("私は元気です。"))
