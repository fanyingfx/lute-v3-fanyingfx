# -*- coding: utf-8 -*-
# version: python 3.5

import sys
import re
from mdict_query.mdict_query import IndexBuilder
from bs4 import BeautifulSoup

# from file_util import *


def process_audio(soup: BeautifulSoup):
    l = soup.find_all("a", {"class": "sound"})
    for a in l:
        a.name = "div"
        a.attrs[
            "onclick"
        ] = "function playAudio(e){e.children[0].play()};playAudio(this)"
        href = a.get("href")
        sound_file = href.split("//")[-1]
        sound_type = sound_file.split(".")[-1]
        audio = soup.new_tag("audio")
        audio.append(soup.new_tag("source", src=sound_file, type=f"audio/{sound_type}"))
        a.append(audio)
        a.attrs.pop("href", None)
    return str(soup)


def get_definition_mdx(word, builder):
    """根据关键字得到MDX词典的解释"""
    print("lookup word: ", word, word == word.strip())
    content = builder.mdx_lookup(word)
    # print('lookup content: ',content)
    if not content:
        content = "".encode("utf-8")
        return content
    pattern = re.compile(r"@@@LINK=(.*)")
    res = []
    for cnt in content:
        rst = pattern.match(cnt)
        if rst is not None:
            link = rst.group(1).strip()
            content = builder.mdx_lookup(link)
        str_content = ""
        if len(content) > 0:
            for c in content:
                str_content += c.replace("\r\n", "").replace("entry:/", "")
        s_html = BeautifulSoup(str_content, "html.parser")
        str_content = process_audio(s_html)

        res.append(str_content)

    output_html = "<br/>".join(res)
    return output_html.encode("utf-8")


def get_definition_mdd(word, builder: IndexBuilder):
    """根据关键字得到MDX词典的媒体"""
    print(f"word: {word}")
    word = word.replace("/", "\\")
    print("word_replace", word)
    content = builder.mdd_lookup(word)
    builder.get_mdd_keys()
    if len(content) > 0:
        return content[0]
    return b""
