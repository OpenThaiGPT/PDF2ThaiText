import re

from .constants import (
    DIGITS,
    TAG_STRIPPER,
)

def thaiDigits(matchobj):
    return DIGITS[matchobj.group(0)]

def strip_tags(html):
    s = TAG_STRIPPER()
    s.feed(html)
    return s.get_data()

def tonemarkPos(matchobj):
    return matchobj.group(2) + matchobj.group(1)

def tonemarkSpace(matchobj):
    return matchobj.group(1) + matchobj.group(2)

def extract_text_from_html(text):
    p2 = re.compile(r'([่้๊๋])([ัุูิีึื])') # <tonemark><vowel> -> <vowel><tonemark>
    p3 = re.compile(r'([ัุูิีึื])\s+([่้๊๋])') # <vowel><space><tonemark> -> <vowel><tonemark>
    p4 = re.compile(r'[ ]+$', re.MULTILINE) # <space>+ -> <space>
    p7 = re.compile(r'\s+(?=[ัุูิีึื])') # <space><vowel> -> <vowel>

    text = strip_tags(text)  # strip html tags
    text = p2.sub(tonemarkPos, text)
    text = p3.sub(tonemarkSpace, text)
    # text = p4.sub(thaiDigits, text)
    text = p4.sub('', text)
    text = p7.sub('', text)
    return text