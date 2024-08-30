import re
import os

from tqdm import tqdm
import thaispellcheck
from attacut import tokenize
from pdf_reader.check_n_shift_tone import check_tone_vowel_sentence, check_tone_vowel_word

def correct_text(txt_file):
    count_wrong_word = 0
    all_word = 0
    all_lines = []

    with open(txt_file, 'r', encoding='utf-8') as f:
        txt = f.read()

    for line in tqdm(txt.split("\n"), desc="Processing lines"):
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
    correct_txt_output = "../corrected_txt_output/"
    os.makedirs(correct_txt_output, exist_ok=True)

    with open(f'{correct_txt_output}{txt_file.split("/")[-1]}', 'w', encoding='utf-8') as f:
        f.write(all_text_lines)