import argparse
from convert_pdf_to_html import process_pdf_to_raw_txt
from pdf_reader.correct_text import correct_text
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="โปรแกรมที่แสดงรายการไฟล์ในโฟลเดอร์")
    parser.add_argument('directory', type=str, help="โฟลเดอร์ที่ต้องการแสดงรายการไฟล์")
    args = parser.parse_args()

    directory = args.directory
    list_of_pdf = os.listdir(args.directory)
    list_of_pdf = [x for x in list_of_pdf if x.endswith('.pdf')]
    list_of_name = [x.replace(".pdf", "") for x in list_of_pdf]

    # Multithreading for processing PDFs
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = {executor.submit(process_pdf_to_raw_txt, directory,list_of_name): pdf_file for pdf_file in list_of_pdf}
        for future in as_completed(futures):
            future.result()

    path_to_raw_txt = "./raw_txt_output/"    
    txt_files = os.listdir(path_to_raw_txt)
    txt_files = [f"{path_to_raw_txt}{txt_file}" for txt_file in txt_files]


    # Multithreading for correcting text
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = [executor.submit(correct_text, txt_file) for txt_file in txt_files]
        for future in as_completed(futures):
            future.result()

  