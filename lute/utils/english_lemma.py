"""
Parsing English and add the lemmatization
"""
import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer


# nltk.download()
WNL = WordNetLemmatizer()


def _get_wordnet_pos(tag):
    if tag.startswith("J"):
        return wordnet.ADJ
    elif tag.startswith("V"):
        return wordnet.VERB
    elif tag.startswith("N"):
        return wordnet.NOUN
    elif tag.startswith("R"):
        return wordnet.ADV


def lemmatize_tokens(tokens):
    """
    Lemmatize the tokens using nltk
    """
    res = []
    for word, pos in nltk.pos_tag(tokens):
        word_pos = _get_wordnet_pos(pos) or wordnet.NOUN
        lemma = WNL.lemmatize(word.lower(), word_pos)
        res.append(lemma)
    return res
