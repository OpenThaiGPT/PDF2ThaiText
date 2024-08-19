import argparse
import os
import subprocess
import html
import re
import pdfplumber
import pandas as pd
import thaispellcheck
from html.parser import HTMLParser
from attacut import tokenize

from concurrent.futures import ThreadPoolExecutor, as_completed

pua = {
    '63233': '&#3636;', # 0xf701 Sara I
    '63234': '&#3637;', # 0xf702
    '63235': '&#3638;', # 0xf703
    '63236': '&#3639;', # 0xf704
    '63237': '&#3656;', # 0xf705
    '63238': '&#3657;', # 0xf706 Mai Tho (on Po Pla)
    '63242': '&#3656;', # 0xf70a Mai Ek
    '63243': '&#3657;', # 0xf70b Mai Tho
    '63246': '&#3660;', # 0xf70e Thantakat
    '63248': '&#3633;', # 0xf710  Mai Han Akhat (on Po Pla)
    '63250': '&#3655;', # 0xf712 Mai Tai Khu (on Po Pla)
    '63251': '&#3656;', # 0xf713
    '63252': '&#3657;', # 0xf714
    '63244': '&#3658;', # ๊
    '63247': '&#3597;', #ญ
    '61482': '&#42;',   #*
    '61591': '&#8226', #•
    '63240': '&#3657', # Mai Tho
    '63241': '&#3652', #Thantakat (on Po Pla)
    '65288': '&#40;', #(
    '65289': '&#41;', #)
    '61623': '&#8226', #•
    '65309': '&#61', #=
    '65293': '&#45', #-
    '65374': '&#126', #~
}
def thaiPUA(input_str, matchobj):
    try:
        return pua[matchobj.group(1)]
    except Exception as e:
        error_message = input_str+":"+str(e)

        try:
            with open('./error_log.txt', 'r', encoding='utf-8') as file:
                error_logs = file.readlines()
        except FileNotFoundError:
            error_logs = []

        if error_message + '\n' not in error_logs:
            with open('./error_log.txt', 'a', encoding='utf-8') as file:
                file.write(error_message + '\n')

        print(error_message)
        return None 

## Convert HTML to TXT
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

digits = {
    '๐': '0',
    '๑': '1',
    '๒': '2',
    '๓': '3',
    '๔': '4',
    '๕': '5',
    '๖': '6',
    '๗': '7',
    '๘': '8',
    '๙': '9'
}

def thaiDigits(matchobj):
    return digits[matchobj.group(0)]

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def tonemarkPos(matchobj):
    return matchobj.group(2) + matchobj.group(1)

def tonemarkSpace(matchobj):
    return matchobj.group(1) + matchobj.group(2)


# your thaiPUA, MLStripper, and other utility functions here
def extract_pages(html_content):
    pages = re.split(r'<div style="page-break-before:always; page-break-after:always">', html_content)
    return pages

### shift tone pupu
tone = [3655, 3656, 3657, 3658, 3659, 3660]
vowel = [3636, 3637, 3638, 3639, 3640, 3641, 3633]


def check_tone_vowel_sentence(new):
    last_check = thaispellcheck.check(new)
    if "คำผิด" in last_check:
        wrong_word = re.findall(r'<คำผิด>(.*?)</คำผิด>', last_check)
        for word in wrong_word:
            word_unicode = [ord(char) for char in word]
            corrected = False
            for i in range(len(word_unicode)):
                if word_unicode[i] in tone or word_unicode[i] in vowel:
                    for j in range(i):
                        if word_unicode[j] not in tone and word_unicode[j] not in vowel:
                            word_unicode[i], word_unicode[j] = word_unicode[j], word_unicode[i]
                                # เช็คคำที่แก้ไขแล้วกับ thaispellcheck
                            new_word = ''.join(chr(c) for c in word_unicode)
                            check_result = thaispellcheck.check(new_word)
                            if "คำผิด" not in check_result:
                                corrected = True
                                break
                            else:
                                    # ย้ายกลับตำแหน่งเดิม
                                word_unicode[i], word_unicode[j] = word_unicode[j], word_unicode[i]
                    if corrected:
                        break

            if corrected:
                new_word = ''.join(chr(c) for c in word_unicode)
                new = new.replace(word, new_word)
    return new                

# shift tone Ko
def check_tone_vowel_word(word):
    tone = [chr(3655), chr(3656), chr(3657), chr(3658), chr(3659), chr(3660)]
    vowel = [chr(3633), chr(3636), chr(3637), chr(3638), chr(3639), chr(3640), chr(3641)]

    def is_tone_or_vowel(char):
        return char in tone or char in vowel

    # Function to move each marker to all possible positions
    def move_markers(word, marker_indices):
        permutations = set()

        def swap(word_list, i, j):
            word_list[i], word_list[j] = word_list[j], word_list[i]
            return word_list

        # Create all permutations by moving each marker to every possible position
        for i, idx in enumerate(marker_indices):
            for pos in range(1,len(word)):
                if pos != idx and not is_tone_or_vowel(word[pos]):
                    new_word = list(word)
                    new_word.insert(pos, new_word.pop(idx))
                    if "คำผิด" not in thaispellcheck.check("".join(new_word)):
                        permutations.add("".join(new_word))
                        return permutations
        permutations.add("")
        return permutations
    # Find the indices of vowels and tone markers
    marker_indices = [i for i, char in enumerate(word) if is_tone_or_vowel(char)]

    # Generate permutations by moving markers
    all_permutations = set()
    all_permutations.update(move_markers(word, marker_indices))
    if list(all_permutations)[0] == "":
        return word
    else:
        return list(all_permutations)[0] 

def process_text(text):
    p2 = re.compile(r'([่้๊๋])([ัุูิีึื])') # <tonemark><vowel> -> <vowel><tonemark>
    p3 = re.compile(r'([ัุูิีึื])\s+([่้๊๋])') # <vowel><space><tonemark> -> <vowel><tonemark>
    p4 = re.compile(r'[ ]+$', re.MULTILINE) # <space>+ -> <space>
    p7 = re.compile(r'\s+(?=[ัุูิีึื])') # <space><vowel> -> <vowel>

    text = strip_tags(text)  # strip html tags
    text = p2.sub(tonemarkPos, text)
    text = p3.sub(tonemarkSpace, text)
    text = p4.sub('', text)
    text = p7.sub('', text)
    return text

def process_pdf(pdf_file, directory):
    path_to_pdf_file = f'{directory}/{pdf_file}.pdf'
    input_format = f'--input={path_to_pdf_file}'

    # Convert PDF to HTML with PDFBox (java)
    output_path = "./html_output/before_mapping"
    os.makedirs(output_path, exist_ok=True)
    command = ['java', '-jar', 'pdfbox-app-3.0.2.jar', 'export:text', '-html', input_format, f'--output={output_path}/{pdf_file}.html']
    subprocess.run(command, capture_output=True, text=True)

    # Mapping some Error Code
    p = re.compile(r'\&\#(6\d{4,})\;')

    output_after_mapping = "./html_output/after_mapping/"
    os.makedirs(output_after_mapping, exist_ok=True)
    with open(f'{output_after_mapping}/{pdf_file}.html', 'w') as outputf:
        with open(f'{output_path}/{pdf_file}.html', 'r') as inputf:
            for line in inputf:
                text = p.sub(lambda match: thaiPUA(f'{output_after_mapping}/{pdf_file}', match), line)
                outputf.writelines(html.unescape(text))

    # Convert HTML to raw text
    with open(f'{output_after_mapping}/{pdf_file}.html', 'r') as inputf:
        text = inputf.read()

    text = process_text(text)
    raw_txt_output = "./raw_txt_output/"
    os.makedirs(raw_txt_output, exist_ok=True)
    with open(f'{raw_txt_output}{pdf_file}.txt', 'w') as outputf:
        outputf.write(text)

    return f'{raw_txt_output}{pdf_file}.txt'

def correct_text(txt_file):
    count_wrong_word = 0
    all_word = 0
    all_lines = []

    with open(txt_file, 'r', encoding='utf-8') as f:
        txt = f.read()

    for line in txt.split("\n"):
        fix_text_line = ""
        if line.strip() != "":
            new = line.replace("ำ", "า")
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
            if re.search(r'([ก-ฮ])า ง', new):
                new = re.sub(r'([ก-ฮ])า ง', r'า\1ง', new)
            if re.search(r'([ก-ฮ])ื อ', new):
                new = re.sub(r'([ก-ฮ])ื อ', r'\1ือ', new)
            if re.search(r'([ก-ฮ])\s้', new):
                new = re.sub(r'([ก-ฮ])\s้', r'\1้', new)
            if re.search(r'([ก-ฮ])\s่', new):
                new = re.sub(r'([ก-ฮ])\s่', r'\1่', new)
            new = new.replace(" า", "ำ")
            new = new.replace("่ื", "ื่")
            new = new.replace("้ื", "ื้")
            new = check_tone_vowel_sentence(new)
            new_line = tokenize(new)
            fix_line = []
            for text in new_line:
                all_word += 1
                if "คำผิด" in thaispellcheck.check(text):
                    text = check_tone_vowel_word(text)
                    fix_line.append(text)
                    if "คำผิด" in thaispellcheck.check(text):
                        count_wrong_word += 1
                else:
                    fix_line.append(text)
            fix_text_line = "".join(fix_line)
        all_lines.append(fix_text_line)
    
    if all_word == 0:
        print(f"can't read this file {txt_file}")
    else:
        print(f"Count wrong word in {txt_file} : {count_wrong_word}/{all_word} % = {count_wrong_word/all_word*100}" )
    
    all_text_lines = "\n".join(all_lines)
    correct_txt_output = "./corrected_txt_output/"
    os.makedirs(correct_txt_output, exist_ok=True)

    with open(f'{correct_txt_output}{txt_file.split("/")[-1]}', 'w', encoding='utf-8') as f:
        f.write(all_text_lines)

def main():
    parser = argparse.ArgumentParser(description="โปรแกรมที่แสดงรายการไฟล์ในโฟลเดอร์")
    parser.add_argument('directory', type=str, help="โฟลเดอร์ที่ต้องการแสดงรายการไฟล์")
    args = parser.parse_args()

    directory = args.directory
    list_of_pdf = os.listdir(args.directory)
    list_of_pdf = [x for x in list_of_pdf if x.endswith('.pdf')]
    list_of_name = [f"{x.split('.')[0]}.{x.split('.')[1]}.{x.split('.')[2]}" for x in list_of_pdf]

    # Multithreading for processing PDFs
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = {executor.submit(process_pdf, pdf_file, directory): pdf_file for pdf_file in list_of_name}
        txt_files = []
        for future in as_completed(futures):
            txt_files.append(future.result())

    # Multithreading for correcting text
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = [executor.submit(correct_text, txt_file) for txt_file in txt_files]
        for future in as_completed(futures):
            future.result()

if __name__ == "__main__":
    main()
