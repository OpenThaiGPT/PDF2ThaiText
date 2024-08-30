import os
import argparse

from concurrent.futures import ThreadPoolExecutor, as_completed
from pdf_reader.pdf_to_raw_txt import process_pdf_to_raw_txt

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