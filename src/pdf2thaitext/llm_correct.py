import os
import re

from tqdm import tqdm
from groq import Groq
import thaispellcheck  # ไลบรารีสำหรับตรวจสอบคำผิดในภาษาไทย

from pdf2thaitext.html_text_utils import map_text_from_html, replace_patterns

def llm_correct(sentence, api_key):
    system='''\
You are a highly skilled language assistant specializing in Thai spelling and grammar corrections. Your task is to read a sentence and correct any spelling, grammar, or punctuation errors. 
Ensure that:
    • All corrections are accurate and relevant to Thai language rules.
    • You provide concise and clear responses without changing the meaning of the sentence.
    • Avoid adding unnecessary details or changing the structure unless it's required for grammatical correctness.

Instructions:
    • Review the sentence carefully.
    • Correct any Thai spelling and grammatical errors.
    • Provide the corrected sentence.\
'''

    query = "Correct the Thai sentence for spelling and grammar."

    client = Groq(api_key=api_key)

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f'''Sentence: {str(sentence)} Questions: {query}'''},
    ]

    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=messages,
        max_tokens=4096,
    )

    return response.choices[0].message.content

def correct_text_with_llm(txt_file,
                          api_key,
                          method):

    if method == "sentence":
        all_lines = []

        with open(txt_file, 'r', encoding='utf-8') as f:
            txt = f.read()

        for line in tqdm(txt.split("\n"), desc="Processing lines"):
            if line.strip() != "":  # ถ้าบรรทัดไม่ว่างเปล่า
                new = line.replace("ำ", "า")  # แทนที่ "ำ" ด้วย "า" ชั่วคราวเพื่อประมวลผล
                new = replace_patterns(new)
                if "คำผิด" in thaispellcheck.check(new):
                    new = llm_correct(new, api_key)
            else:
                continue
            all_lines.append(new)

        all_text_lines = "\n".join(all_lines)
    elif method == "page":
        llm_pages = []
        is_correct = True
        #chang PathToText to PathToHtml
        html_file = txt_file.replace(".txt", ".html")
        html_file = html_file.replace("raw_txt_output", "html_output")
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        pages = re.split(r'<div style="page-break-before:always; page-break-after:always">', html_content)
        for page in tqdm(pages, desc="Processing pages"):
            raw_text = map_text_from_html(page)
            if raw_text.strip() == "": # ป้องกันกรณีที่หน้าว่าง
                continue
            all_lines = []
            for line in raw_text.split("\n"):
                if line.strip() != "":  # ถ้าบรรทัดไม่ว่างเปล่า
                    new = line.replace("ำ", "า")  # แทนที่ "ำ" ด้วย "า" ชั่วคราวเพื่อประมวลผล
                    new = replace_patterns(new)
                    if "คำผิด" in thaispellcheck.check(new):
                        is_correct = False
                    all_lines.append(new)
                else:
                    continue
            page_content = "\n".join(all_lines)
            if is_correct:
                llm_content = llm_correct(page_content, api_key)
            else:
                llm_content = page_content
            llm_pages.append(llm_content)
        all_text_lines = "\n".join(llm_pages)
            
    correct_txt_output = "./corrected_txt_output/"
    os.makedirs(correct_txt_output, exist_ok=True)  # สร้างโฟลเดอร์หากยังไม่มี

    with open(f'{correct_txt_output}{txt_file.split("/")[-1]}', 'w', encoding='utf-8') as f:
        f.write(all_text_lines)  # บันทึกผลลัพธ์ที่แก้ไขแล้วลงในไฟล์ใหม่
