import re
import os
from tqdm import tqdm  # ใช้สำหรับแสดงแถบความคืบหน้าในกระบวนการประมวลผล
import thaispellcheck  # ไลบรารีสำหรับตรวจสอบคำผิดในภาษาไทย
from attacut import tokenize  # ไลบรารีสำหรับการตัดคำในภาษาไทย
from pdf2thaitext.check_n_shift_tone import check_tone_vowel_sentence, check_tone_vowel_word  # ฟังก์ชันตรวจสอบและแก้ไขวรรณยุกต์และสระ

def correct_text(txt_file):
    """
    ฟังก์ชันนี้ใช้สำหรับแก้ไขข้อความในไฟล์ .txt โดยตรวจสอบและแก้ไขคำที่มีการใช้วรรณยุกต์และสระที่ผิด
    และนับจำนวนคำที่ผิด
    
    Args:
        txt_file (str): เส้นทางไปยังไฟล์ข้อความที่ต้องการแก้ไข
        
    Returns:
        None: ผลลัพธ์จะถูกบันทึกลงในไฟล์ข้อความใหม่ในโฟลเดอร์ 'corrected_txt_output'
    """
    
    count_wrong_word = 0  # ตัวนับจำนวนคำที่ผิด
    all_word = 0  # ตัวนับจำนวนคำทั้งหมด
    all_lines = []  # รายการเก็บบรรทัดทั้งหมดหลังจากแก้ไขแล้ว

    # อ่านไฟล์ข้อความที่กำหนด
    with open(txt_file, 'r', encoding='utf-8') as f:
        txt = f.read()

    # ประมวลผลข้อความทีละบรรทัด
    for line in tqdm(txt.split("\n"), desc="Processing lines"):
        fix_text_line = ""
        if line.strip() != "":  # ถ้าบรรทัดไม่ว่างเปล่า
            new = line.replace("ำ", "า")  # แทนที่ "ำ" ด้วย "า" ชั่วคราวเพื่อประมวลผล
            # ใช้ regular expressions แทนที่รูปแบบที่ผิดด้วยรูปแบบที่ถูก
            if re.search(r'([ก-ฮ])ํ า', new):
                new = re.sub(r'([ก-ฮ])ํ า', r'\1ำ', new)
            if re.search(r'([ก-ฮ])่ า', new):
                new = re.sub(r'([ก-ฮ])่ า', r'\1่า', new)
            if re.search(r'([ก-ฮ])้ า', new):
                new = re.sub(r'([ก-ฮ])้ า', r'\1้า', new)
            if re.search(r'([ก-ฮ])๊ า', new):
                new = re.sub(r'([ก-ฮ])๊ า', r'\1๊า', new)
            if re.search(r'([ก-ฮ])๋ า', new):
                new = re.sub(r'([ก-ฮ])๋ า', r'\1๋า', new)
            if re.search(r'([ก-ฮ]) ำ', new):
                new = re.sub(r'([ก-ฮ]) ำ', r'\1ำ', new)
            if re.search(r'([ก-ฮ])า ง', new):
                new = re.sub(r'([ก-ฮ])า ง', r'า\1ง', new)
            if re.search(r'([ก-ฮ])ื อ', new):
                new = re.sub(r'([ก-ฮ])ื อ', r'\1ือ', new)
            if re.search(r'([ก-ฮ])\s้', new):
                new = re.sub(r'([ก-ฮ])\s้', r'\1้', new)
            if re.search(r'([ก-ฮ])\s่', new):
                new = re.sub(r'([ก-ฮ])\s่', r'\1่', new)
            new = new.replace(" า", "ำ")  # แทนที่ " า" ด้วย "ำ" อีกครั้ง
            new = new.replace("่ื", "ื่")  # แก้ไขวรรณยุกต์ผิดที่
            new = new.replace("้ื", "ื้")
            new = check_tone_vowel_sentence(new)  # ตรวจสอบและแก้ไขวรรณยุกต์และสระในประโยค
            new_line = tokenize(new)  # ตัดคำในประโยค
            fix_line = []
            for text in new_line:
                all_word += 1
                if "คำผิด" in thaispellcheck.check(text):  # ตรวจสอบว่ามีคำผิดหรือไม่
                    text = check_tone_vowel_word(text)  # แก้ไขคำที่ผิด
                    fix_line.append(text)
                    if "คำผิด" in thaispellcheck.check(text):
                        count_wrong_word += 1  # นับจำนวนคำที่ยังผิดหลังจากแก้ไข
                else:
                    fix_line.append(text)
            fix_text_line = "".join(fix_line)
        all_lines.append(fix_text_line)
    
    if all_word == 0:
        print(f"can't read this file {txt_file}")  # แสดงข้อความเมื่อไม่สามารถอ่านไฟล์ได้
    else:
        print(f"Count wrong word in {txt_file} : {count_wrong_word}/{all_word} % = {count_wrong_word/all_word*100}")  # แสดงจำนวนคำที่ผิดและเปอร์เซ็นต์
    
    all_text_lines = "\n".join(all_lines)
    correct_txt_output = "./corrected_txt_output/"
    os.makedirs(correct_txt_output, exist_ok=True)  # สร้างโฟลเดอร์หากยังไม่มี

    with open(f'{correct_txt_output}{txt_file.split("/")[-1]}', 'w', encoding='utf-8') as f:
        f.write(all_text_lines)  # บันทึกผลลัพธ์ที่แก้ไขแล้วลงในไฟล์ใหม่
