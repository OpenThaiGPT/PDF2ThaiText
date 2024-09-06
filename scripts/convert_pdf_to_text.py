import argparse
from pdf2thaitext.pdf_to_raw_txt import process_pdf_to_raw_txt
from pdf2thaitext.correct_text import correct_text
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

if __name__ == "__main__":
    """
    สคริปต์นี้ใช้สำหรับแปลงไฟล์ PDF ในโฟลเดอร์ที่กำหนดเป็นไฟล์ข้อความดิบ (raw text)
    และแก้ไขข้อความที่ได้จากไฟล์ข้อความนั้น
    """
    
    # การตั้งค่าคำสั่งในการใช้สคริปต์
    parser = argparse.ArgumentParser(description="โปรแกรมที่แสดงรายการไฟล์ในโฟลเดอร์")
    parser.add_argument('directory', type=str, help="โฟลเดอร์ที่ต้องการแสดงรายการไฟล์")
    args = parser.parse_args()

    directory = args.directory  # โฟลเดอร์ที่ระบุโดยผู้ใช้
    list_of_pdf = os.listdir(args.directory)  # ดึงรายการชื่อไฟล์ทั้งหมดในโฟลเดอร์ที่กำหนด
    list_of_pdf = [x for x in list_of_pdf if x.endswith('.pdf')]  # กรองเฉพาะไฟล์ PDF
    list_of_name = [x.replace(".pdf", "") for x in list_of_pdf]  # ลบ .pdf ออกจากชื่อไฟล์

    # ใช้ Multithreading เพื่อประมวลผลไฟล์ PDF
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        # สร้าง futures สำหรับแต่ละไฟล์ PDF โดยเรียกใช้งานฟังก์ชัน process_pdf_to_raw_txt
        futures = {executor.submit(process_pdf_to_raw_txt, directory, list_of_name): pdf_file for pdf_file in list_of_pdf}
        for future in as_completed(futures):
            future.result()  # ดึงผลลัพธ์จาก future (ในที่นี้คือไม่มีการนำผลลัพธ์ไปใช้ต่อ)

    path_to_raw_txt = "./raw_txt_output/"  # เส้นทางไปยังโฟลเดอร์ที่เก็บไฟล์ข้อความดิบ
    txt_files = os.listdir(path_to_raw_txt)  # ดึงรายการชื่อไฟล์ทั้งหมดในโฟลเดอร์ที่กำหนด
    txt_files = [f"{path_to_raw_txt}{txt_file}" for txt_file in txt_files]  # สร้างรายการเส้นทางไฟล์ข้อความทั้งหมด

    # ใช้ Multithreading เพื่อแก้ไขข้อความ
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        # สร้าง futures สำหรับแต่ละไฟล์ข้อความในรายการ โดยเรียกใช้งานฟังก์ชัน correct_text
        futures = [executor.submit(correct_text, txt_file) for txt_file in txt_files]
        for future in as_completed(futures):
            future.result()  # ดึงผลลัพธ์จาก future (ในที่นี้คือไม่มีการนำผลลัพธ์ไปใช้ต่อ)
    
    print("เสร็จสิ้นการแปลงไฟล์ PDF เป็นไฟล์ข้อความดิบและแก้ไขข้อความ")
