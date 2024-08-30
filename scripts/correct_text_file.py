import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pdf_reader.correct_text import correct_text

if __name__ == "__main__":
    path_to_output = "../raw_txt_output/"
    list_of_name = os.listdir(path_to_output)
    list_of_raw_txts = [f"{path_to_output}{txt_file}" for txt_file in list_of_name]
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = [executor.submit(correct_text, txt_file) for txt_file in list_of_raw_txts]
        for future in as_completed(futures):
            future.result()