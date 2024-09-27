import re
from .constants import (
    DIGITS,
    TAG_STRIPPER,
)

def thaiDigits(matchobj):
    """
    ฟังก์ชันนี้ใช้แทนที่ตัวเลขไทยด้วยตัวเลขอารบิก

    Args:
        matchobj: วัตถุที่ตรงกับรูปแบบ regex (regular expression)
    
    Returns:
        str: ตัวเลขอารบิกที่สอดคล้องกับตัวเลขไทย
    """
    return DIGITS[matchobj.group(0)]

def strip_tags(html):
    """
    ฟังก์ชันนี้ใช้ลบแท็ก HTML ออกจากข้อความ

    Args:
        html (str): ข้อความ HTML ที่ต้องการลบแท็กออก
    
    Returns:
        str: ข้อความที่ไม่มีแท็ก HTML
    """
    s = TAG_STRIPPER()
    s.feed(html)
    return s.get_data()

def tonemarkPos(matchobj):
    """
    ฟังก์ชันนี้ใช้สลับตำแหน่งของวรรณยุกต์และสระ

    Args:
        matchobj: วัตถุที่ตรงกับรูปแบบ regex (regular expression)
    
    Returns:
        str: ข้อความที่สลับตำแหน่งวรรณยุกต์และสระ
    """
    return matchobj.group(2) + matchobj.group(1)

def tonemarkSpace(matchobj):
    """
    ฟังก์ชันนี้ใช้ลบช่องว่างระหว่างสระและวรรณยุกต์

    Args:
        matchobj: วัตถุที่ตรงกับรูปแบบ regex (regular expression)
    
    Returns:
        str: ข้อความที่ลบช่องว่างระหว่างสระและวรรณยุกต์
    """
    return matchobj.group(1) + matchobj.group(2)

def replace_patterns(text):
    """
    ฟังก์ชันนี้ใช้แทนที่รูปแบบที่ผิดด้วยรูปแบบที่ถูก

    Args:
        text (str): ข้อความที่ต้องการแทนที่รูปแบบที่ผิด
    
    Returns:
        str: ข้อความที่แทนที่รูปแบบที่ผิดด้วยรูปแบบที่ถูกแล้ว
    """
    patterns = [
        (r'([ก-ฮ])ํ า', r'\1ำ'),
        (r'([ก-ฮ])่ า', r'\1่า'),
        (r'([ก-ฮ])้ า', r'\1้า'),
        (r'([ก-ฮ])๊ า', r'\1๊า'),
        (r'([ก-ฮ])๋ า', r'\1๋า'),
        (r'([ก-ฮ]) ำ', r'\1ำ'),
        (r'([ก-ฮ])า ง', r'า\1ง'),
        (r'([ก-ฮ])ื อ', r'\1ือ'),
        (r'([ก-ฮ])\s้', r'\1้'),
        (r'([ก-ฮ])\s่', r'\1่')
    ]
    
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)
    
    text = text.replace(" า", "ำ")
    text = text.replace("่ื", "ื่")
    text = text.replace("้ื", "ื้")
    
    return text

def map_text_from_html(text):
    """
    ฟังก์ชันนี้ใช้สำหรับแยกข้อความจาก HTML และแก้ไขการใช้วรรณยุกต์และสระให้ถูกต้อง

    Args:
        text (str): ข้อความ HTML ที่ต้องการแยกและแก้ไข
    
    Returns:
        str: ข้อความที่แยกจาก HTML และแก้ไขการใช้วรรณยุกต์และสระแล้ว
    """
    p1 = re.compile(r'[๐๑๒๓๔๕๖๗๘๙]') # thai digits -> arabic digits
    p2 = re.compile(r'([่้๊๋])([ัุูิีึื])')  # แพทเทิร์นสำหรับสลับตำแหน่งวรรณยุกต์และสระ
    p3 = re.compile(r'([ัุูิีึื])\s+([่้๊๋])')  # แพทเทิร์นสำหรับลบช่องว่างระหว่างสระและวรรณยุกต์
    p4 = re.compile(r'[ ]+$', re.MULTILINE)  # แพทเทิร์นสำหรับลบช่องว่างที่ท้ายบรรทัด
    p7 = re.compile(r'\s+(?=[ัุูิีึื])')  # แพทเทิร์นสำหรับลบช่องว่างหน้าสระ

    text = strip_tags(text)  # ลบแท็ก HTML ออกจากข้อความ
    text = p1.sub(thaiDigits, text)  # แปลงตัวเลขไทยเป็นตัวเลขอารบิก
    text = p2.sub(tonemarkPos, text)  # สลับตำแหน่งวรรณยุกต์และสระ
    text = p3.sub(tonemarkSpace, text)  # ลบช่องว่างระหว่างสระและวรรณยุกต์
    text = p4.sub('', text)  # ลบช่องว่างที่ท้ายบรรทัด
    text = p7.sub('', text)  # ลบช่องว่างหน้าสระ
    return text
