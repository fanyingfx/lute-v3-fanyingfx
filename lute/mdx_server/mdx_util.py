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
    rst = pattern.match(content[0])
    # import ipdb
    # ipdb.set_trace()
    if rst is not None:
        link = rst.group(1).strip()
        content = builder.mdx_lookup(link)
    str_content = ""
    if len(content) > 0:
        for c in content:
            str_content += c.replace("\r\n", "").replace("entry:/", "")

    injection = []
    injection_html = ""
    output_html = ""

    # try:
    #     # PyInstaller creates a temp folder and stores path in _MEIPASS
    #     # base_path = sys._MEIPASS
    #     base_path = os.path.dirname(sys.executable)
    # except Exception:
    #     base_path = os.path.abspath(".")

    # resource_path = os.path.join(base_path, 'mdx')

    # file_util_get_files(resource_path, injection)

    # for p in injection:
    #     if file_util_is_ext(p, 'html'):
    #         injection_html += file_util_read_text(p)
    # if injection_html!='':
    #     print('injection is not null',injection_html)

    # return [bytes(str_content, encoding='utf-8')]
    output_html = str_content + injection_html
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
