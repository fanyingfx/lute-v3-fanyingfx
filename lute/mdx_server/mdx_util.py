# -*- coding: utf-8 -*-
# version: python 3.5

import sys
import re
from mdict_query.mdict_query import IndexBuilder

# from file_util import *


def get_definition_mdx(word, builder):
    """根据关键字得到MDX词典的解释"""
    print("lookup word: ", word, word == word.strip())
    content = builder.mdx_lookup(word)
    # print('lookup content: ',content)
    if not content:
        content = "".encode("utf-8")
        return content
    # print(word,content)
    # if len(content) < 1:
    # fp = os.popen('python lemma.py ' + word)
    # word = fp.read().strip()
    # fp.close()
    # print("lemma: " + word)
    # content = builder.mdx_lookup(word)
    # pattern = re.compile(r"@@@LINK=([\w\s]*)")
    pattern = re.compile(r"@@@LINK=(.*)")
    res = []
    for cnt in content:
        rst = pattern.match(cnt)
        # import ipdb
        # ipdb.set_trace()
        if rst is not None:
            link = rst.group(1).strip()
            content = builder.mdx_lookup(link)
        str_content = ""
        if len(content) > 0:
            for c in content:
                str_content += c.replace("\r\n", "").replace("entry:/", "")
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
