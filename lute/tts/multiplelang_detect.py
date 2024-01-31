# from aspeak import SpeechService
# https://github.com/zafercavdar/fasttext-langdetect
# import ftlangdetect
import re
import string

from langdetect import detect
from langdetect import detect_langs

# service = SpeechService(region='eastasia',key='39931e505d9842e3bdc9ff87fc46eb96')
remove_nota = "[’·°–!\"#$%&'()*+,-./:;<=>?@，。?★、…【】（）《》？“”‘’！[\\]^_`{|}~]+"
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)


def filter_str(sentence):
    sentence = re.sub(remove_nota, "", sentence)
    sentence = sentence.translate(remove_punctuation_map)
    return sentence.strip()


# 判断中日韩英
def judge_language(s):
    # s = unicode(s)   # python2需要将字符串转换为unicode编码，python3不需要
    s = filter_str(s)
    result = []
    s = re.sub("[0-9]", "", s).strip()
    # unicode english
    re_words = re.compile("[a-zA-Z]")
    res = re.findall(re_words, s)  # 查询出所有的匹配字符串
    res2 = re.sub("[a-zA-Z]", "", s).strip()
    if len(res) > 0:
        result.append("en")
    if len(res2) <= 0:
        return "en"
    # unicode chinese
    re_words = re.compile("[\u4e00-\u9fa5]+")
    res = re.findall(re_words, s)  # 查询出所有的匹配字符串
    res2 = re.sub("[\u4e00-\u9fa5]+", "", s).strip()
    if len(res) > 0:
        result.append("zh")
    if len(res2) <= 0:
        return "zh"
    # unicode korean
    re_words = re.compile("[\uac00-\ud7ff]+")
    res = re.findall(re_words, s)  # 查询出所有的匹配字符串
    res2 = re.sub("[\uac00-\ud7ff]+", "", s).strip()
    if len(res) > 0:
        result.append("ko")
    if len(res2) <= 0:
        return "ko"
    # unicode japanese katakana and unicode japanese hiragana
    re_words = re.compile("[\u30a0-\u30ff\u3040-\u309f]+")
    res = re.findall(re_words, s)  # 查询出所有的匹配字符串
    res2 = re.sub("[\u30a0-\u30ff\u3040-\u309f]+", "", s).strip()
    if len(res) > 0:
        result.append("ja")
    if len(res2) <= 0:
        return "ja"
    return ",".join(result)


lang_dict = {"ja": "ja-JP", "zh-cn": "zh-CN", "en": "en-US"}


def get_lang(s):
    lang = detect(s)
    jl = judge_language(s)
    if jl == "en":
        return jl
    if lang == "ko":
        for _ in range(3):
            if "zh-cn" in [x.lang for x in detect_langs(s)]:
                lang = "zh-cn"
                break
        if lang != "zh-cn":
            for _ in range(3):
                if "ja" in [x.lang for x in detect_langs(s)]:
                    lang = "ja"
                    break
    if lang == "ja" and "ja" in jl:
        lang = "ja"
    elif jl == "zh" and lang == "ja":
        lang = "zh-cn"
    return lang
