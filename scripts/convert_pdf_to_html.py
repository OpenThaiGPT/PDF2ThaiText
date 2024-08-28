import argparse
import os
import re
import html
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

from pdf_reader.constants import PUA
from pdf_reader.extract_text_from_html import extract_text_from_html

def convert_pdf_to_html(directory,list_of_name):
    for num in range(len(list_of_name)):
        pdf_file = list_of_name[num]
        path_to_pdf_file = f'{directory}/{pdf_file}.pdf'
        input_format = '--input='+path_to_pdf_file
        output_path = "../html_output"
        os.makedirs(output_path, exist_ok=True)
        # คำสั่งที่ต้องการรัน
        command = ['java', '-jar', '../src/pdf_reader/pdfbox-app-3.0.2.jar', 'export:text', '-html', input_format, f'--output={output_path}/{list_of_name[num]}.html']

        # รันคำสั่งและเก็บผลลัพธ์
        subprocess.run(command, capture_output=True, text=True)
        return output_path
    
def thaiPUA(matchobj):
    return PUA[matchobj.group(1)]


def map_error(output_path,list_of_name):
    
    p = re.compile(r'\&\#(6\d{4,})\;')

    for num in range(len(list_of_name)):
        inputf = open(f'{output_path}/{list_of_name[num]}.html', 'r')
        after_map = []
        for line in inputf:
            text = p.sub(thaiPUA, line)
            after_map.append(html.unescape(text))
        return "".join(after_map)


def convert_html_to_txt(after_map,list_of_name):
    for num in range(len(list_of_name)):
        text = extract_text_from_html(after_map)
        os.makedirs('../raw_txt_output', exist_ok=True)
        with open(f'../raw_txt_output/{list_of_name[num]}.txt', 'w', encoding='utf-8') as outputf:
            outputf.write(text)


def process_pdf_to_raw_txt(directory,list_of_name):
    output_path = convert_pdf_to_html(directory, list_of_name)
    after_map = map_error(output_path, list_of_name)
    convert_html_to_txt(after_map, list_of_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="โปรแกรมที่แสดงรายการไฟล์ในโฟลเดอร์")
    parser.add_argument('directory', type=str, help="โฟลเดอร์ที่ต้องการแสดงรายการไฟล์")
    args = parser.parse_args()

    directory = args.directory
    list_of_pdf = os.listdir(args.directory)
    list_of_pdf = [x for x in list_of_pdf if x.endswith('.pdf')]
    list_of_name = [x.replace(".pdf", "") for x in list_of_pdf]

    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = {executor.submit(process_pdf_to_raw_txt,directory,list_of_name): pdf_file for pdf_file in list_of_pdf}