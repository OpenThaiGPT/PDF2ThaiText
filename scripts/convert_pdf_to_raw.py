import os
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pdf2thaitext.pdf_to_raw_txt import process_pdf_to_raw_txt

if __name__ == "__main__":
    """
    สคริปต์นี้ใช้สำหรับแปลงไฟล์ PDF ที่อยู่ในโฟลเดอร์ที่กำหนดเป็นไฟล์ข้อความดิบ (raw text)
    โดยใช้การประมวลผลแบบขนานเพื่อเพิ่มประสิทธิภาพในการทำงาน
    """
    
    # ตั้งค่าคำสั่งในการใช้สคริปต์ผ่าน command-line
    parser = argparse.ArgumentParser(description="โปรแกรมที่แสดงรายการไฟล์ในโฟลเดอร์")
    parser.add_argument(
        '--directory',
        type=str,
        help="โฟลเดอร์ที่ต้องการแสดงรายการไฟล์"
    )

    args = parser.parse_args()

    directory = args.directory  # กำหนดโฟลเดอร์ที่ต้องการใช้
    list_of_pdf = os.listdir(args.directory)  # ดึงรายการชื่อไฟล์ทั้งหมดในโฟลเดอร์ที่กำหนด
    list_of_pdf = [x for x in list_of_pdf if x.endswith('.pdf')]  # กรองเฉพาะไฟล์ PDF
    list_of_name = [x.replace(".pdf", "") for x in list_of_pdf]  # สร้างรายการชื่อไฟล์โดยตัด ".pdf" ออก

    # ใช้ ThreadPoolExecutor เพื่อประมวลผลไฟล์ PDF แบบขนาน
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        # สร้าง futures สำหรับแต่ละไฟล์ PDF โดยเรียกใช้งานฟังก์ชัน process_pdf_to_raw_txt
        futures = {executor.submit(process_pdf_to_raw_txt, directory, list_of_name): pdf_file for pdf_file in list_of_pdf}

        # รอให้ทุกฟังก์ชันที่ส่งไปใน future เสร็จสิ้นการทำงาน
        for future in as_completed(futures):
            result = future.result()  # ดึงผลลัพธ์จาก future (ในที่นี้คือไม่มีการนำผลลัพธ์ไปใช้ต่อ)

