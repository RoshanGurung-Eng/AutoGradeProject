# text_correction.py

import re
import json
import os
from nltk.corpus import words
from fuzzywuzzy import fuzz
from .config import OOAD_VOCAB

# Load English dictionary once
ENGLISH_WORDS = set(w.lower() for w in words.words())

# Default manual fixes
DEFAULT_OCR_FIXES = {
    "Dui": "The", "Hie": "The", "Tne": "The", "Tre": "The", "He": "the", "he": "the",
    "Ruge": "four", "choraclevskcs": "characteristics", "cstbus": "systems", "fey": "of",
    "Ibuled": "published", "cC": "or", "chovrcleush": "concurrency", "slx": "is",
    "horcleoa": "hardware", "sAco": "software", "Vo": "to", "Resaur": "resource",
    "ce": "sharing", "Shan": "sharing", "nel": "and", "elaki": "data", "baeheen": "between",
    "usens": "use", "rnterapelal": "interoperable", "Gan": "can", "Can": "can",
    "Jrenolecl": "extended", "Jnrugh": "through", "lsheel": "published", "itefces": "interfaces",
    "Fents": "components", "an": "and", "@an": "and", "@Cces": "access", "Cces": "access",
    "Shored": "shared", "iaovr": "in", "(onWun": "concurrency", "onWun": "concurrency",
    "enc": "concurrency", "Knue": "need", "4o": "to", "peryurm": "perform", "anc": "and",
    "lem": "them", "Sca": "scalability", "cohan": "concurrent", "Scelec)": "scalability",
    "Scelec": "scalability", "Sff1": "efficient", "Sff": "efficient", "k(": "when",
    "m1ct": "scaled", "dssk": "task", "Laplan": "parallel", "Oncun": "concurrency",
    "cte": "and", "Daec": "data", "Daec@s": "data", "aal": "all", "SYstem": "system",
    "~System": "system", "Opennes": "openness", "Pob-": "property", "mony": "many",
    "tex": "next", "'lab_": "label", "lab": "label", "en": "and", "en/": "and",
    # Noise cleanup
    "8": "", "0": "", "6e": "be", "€": "", "$": "", "~J": "", "@": "", "5": "", "/": "",
    "'": "", "_": "", ".": "", "(": "", ")": "", "r": "", "c": "", "s": "", "k": "",
    "ct": "", "stem": "system", "4stem": "system", "24k": "up", "UP": "up", "'lab": "label",
    "4o_peryurm": "to perform"
}

def clean_word_for_ocr(word):
    word = re.sub(r'^[^a-zA-Z]+', '', word)
    word = re.sub(r'[^a-zA-Z]+$', '', word)
    return word

def is_real_english_word(word):
    clean = clean_word_for_ocr(word)
    return len(clean) > 0 and clean.lower() in ENGLISH_WORDS

def correct_to_ooad_term(word, vocab=OOAD_VOCAB, threshold=65):
    clean = clean_word_for_ocr(word)
    if len(clean) == 0:
        return word
    best_match, best_score = word, 0
    for term in vocab:
        score = fuzz.ratio(clean.lower(), term.lower())
        if score > best_score:
            best_score, best_match = score, term
    return best_match if best_score >= threshold else word

def safe_correct_word(word, ocr_fixes):
    if word in ocr_fixes:
        fixed = ocr_fixes[word]
        return fixed if fixed else ""
    if is_real_english_word(word):
        return word
    return correct_to_ooad_term(word)

def auto_build_ocr_fixes(student_words, model_words, threshold=65):
    fixes = {}
    for s_word in student_words:
        s_clean = re.sub(r'[^a-zA-Z]', '', s_word).lower()
        if len(s_clean) < 3 or s_clean in ENGLISH_WORDS:
            continue
        best_match, best_score = None, 0
        for m_word in model_words:
            score = fuzz.ratio(s_clean, m_word.lower())
            if score > best_score:
                best_score, best_match = score, m_word
        if best_score >= threshold and best_match and best_match != s_clean:
            fixes[s_word] = best_match
    return fixes