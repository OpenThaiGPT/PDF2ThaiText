import os
import re
import html
import subprocess

from pdf_reader.constants import PUA, PATH_TO_PDF_BOX
from pdf_reader.html_text_utils import map_text_from_html

def convert_pdf_to_html(directory, list_of_name):
    """
    ฟังก์ชันนี้ใช้สำหรับแปลงไฟล์ PDF เป็นไฟล์ HTML โดยใช้ PDFBox

    Args:
        directory (str): เส้นทางไปยังโฟลเดอร์ที่เก็บไฟล์ PDF
        list_of_name (list): รายการชื่อไฟล์ PDF ที่ต้องการแปลง
    
    Returns:
        str: เส้นทางไปยังโฟลเดอร์ที่เก็บไฟล์ HTML ที่แปลงแล้ว
    """
    for num in range(len(list_of_name)):
        pdf_file = list_of_name[num]
        path_to_pdf_file = f'{directory}/{pdf_file}.pdf'
        input_format = '--input=' + path_to_pdf_file
        output_path = "./html_output"
        os.makedirs(output_path, exist_ok=True)  # สร้างโฟลเดอร์สำหรับเก็บไฟล์ HTML ถ้ายังไม่มี

        # คำสั่งที่ต้องการรัน
        command = ['java', '-jar', PATH_TO_PDF_BOX, 'export:text', '-html', input_format, f'--output={output_path}/{list_of_name[num]}.html']

        # รันคำสั่งและเก็บผลลัพธ์
        subprocess.run(command, capture_output=True, text=True)
    
    return output_path

def thai_pua(matchobj):
    """
    ฟังก์ชันนี้ใช้แทนที่รหัส PUA ด้วยตัวอักษร Unicode ที่สอดคล้องกัน

    Args:
        matchobj: วัตถุที่ตรงกับรูปแบบ regex (regular expression)
    
    Returns:
        str: ตัวอักษร Unicode ที่สอดคล้องกับรหัส PUA
    """
    return PUA[matchobj.group(1)]

def map_error(output_path, list_of_name):
    """
    ฟังก์ชันนี้ใช้สำหรับการแปลงรหัส PUA ในไฟล์ HTML เป็นตัวอักษร Unicode

    Args:
        output_path (str): เส้นทางไปยังโฟลเดอร์ที่เก็บไฟล์ HTML
        list_of_name (list): รายการชื่อไฟล์ HTML ที่ต้องการแปลง
    
    Returns:
        str: ข้อความที่ได้รับการแปลงรหัส PUA เป็น Unicode แล้ว
    """
    p = re.compile(r'\&\#(6\d{4,})\;')  # รูปแบบ regex สำหรับจับรหัส PUA

    for num in range(len(list_of_name)):
        inputf = open(f'{output_path}/{list_of_name[num]}.html', 'r')
        after_map = []
        for line in inputf:
            text = p.sub(thai_pua, line)  # แทนที่รหัส PUA ด้วยตัวอักษร Unicode
            after_map.append(html.unescape(text))  # แปลง HTML entities เป็นตัวอักษร
        inputf.close()
        return "".join(after_map)

def convert_html_to_txt(after_map, list_of_name):
    """
    ฟังก์ชันนี้ใช้สำหรับแปลงข้อความในรูปแบบ HTML เป็นไฟล์ข้อความ (.txt)

    Args:
        after_map (str): ข้อความ HTML ที่ได้รับการแปลงรหัส PUA เป็น Unicode แล้ว
        list_of_name (list): รายการชื่อไฟล์ที่ต้องการแปลง
    
    Returns:
        None: สร้างไฟล์ .txt ที่มีข้อความที่แปลงแล้ว
    """
    for num in range(len(list_of_name)):
        text = map_text_from_html(after_map)  # ดึงข้อความจาก HTML และแก้ไข
        os.makedirs('./raw_txt_output', exist_ok=True)  # สร้างโฟลเดอร์สำหรับเก็บไฟล์ข้อความถ้ายังไม่มี
        with open(f'./raw_txt_output/{list_of_name[num]}.txt', 'w', encoding='utf-8') as outputf:
            outputf.write(text)

def process_pdf_to_raw_txt(directory, list_of_name):
    """
    ฟังก์ชันหลักที่ใช้ในการแปลงไฟล์ PDF เป็นไฟล์ข้อความ (.txt) โดยผ่านกระบวนการแปลงเป็น HTML ก่อน

    Args:
        directory (str): เส้นทางไปยังโฟลเดอร์ที่เก็บไฟล์ PDF
        list_of_name (list): รายการชื่อไฟล์ PDF ที่ต้องการแปลง
    
    Returns:
        None: สร้างไฟล์ .txt ที่มีข้อความที่แปลงแล้ว
    """
    output_path = convert_pdf_to_html(directory, list_of_name)  # แปลง PDF เป็น HTML
    after_map = map_error(output_path, list_of_name)  # แปลงรหัส PUA เป็น Unicode
    convert_html_to_txt(after_map, list_of_name)  # แปลง HTML เป็น .txt
