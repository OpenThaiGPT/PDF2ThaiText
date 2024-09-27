import os
import argparse

from concurrent.futures import ThreadPoolExecutor, as_completed
from pdf2thaitext.correct_text import correct_text
from pdf2thaitext.llm_correct import correct_text_with_llm

if __name__ == "__main__":
    """
    สคริปต์นี้ใช้ในการอ่านไฟล์ข้อความที่ถูกเก็บไว้ในโฟลเดอร์ที่กำหนด และดำเนินการแก้ไขข้อความ
    โดยใช้ฟังก์ชัน correct_text และทำงานแบบขนานเพื่อเพิ่มประสิทธิภาพในการประมวลผล
    """
    parser = argparse.ArgumentParser(description="โปรแกรมที่แสดงรายการไฟล์ในโฟลเดอร์")
    parser.add_argument(
        '--with-llm',
        type=str,
        default="",
        help="ใช้โมเดล LLM ในการแก้ไขข้อความหรือไม่"
    )
    parser.add_argument(
        '--method',
        type=str,
        default="page",
        help="วิธีการแก้ไขข้อความ (page, sentence)"
    )
    parser.add_argument(
        '--model',
        type=str,
        default="llama-3.1-70b-versatile",
        help="ชื่อโมเดลที่ใช้ในการแก้ไขข้อความ"
    )
    parser.add_argument(
        '--num-proc',
        type=int,
        default=os.cpu_count(),
        help="จำนวนเธรดที่ใช้ในการประมวลผลข้อมูล"
    )
    args = parser.parse_args()

    path_to_output = "../raw_txt_output/"  # เส้นทางไปยังโฟลเดอร์ที่เก็บไฟล์ข้อความที่ยังไม่ได้แก้ไข
    list_of_name = os.listdir(path_to_output)  # ดึงรายการชื่อไฟล์ทั้งหมดในโฟลเดอร์ที่กำหนด
    list_of_raw_txts = [f"{path_to_output}{txt_file}" for txt_file in list_of_name]  # สร้างรายการเส้นทางไฟล์ข้อความทั้งหมด
    
    if args.with_llm == "":
        # ใช้ ThreadPoolExecutor เพื่อดำเนินการฟังก์ชัน correct_text แบบขนาน
        with ThreadPoolExecutor(max_workers=args.num_proc) as executor:
            # สร้าง futures สำหรับแต่ละไฟล์ข้อความในรายการ โดยเรียกใช้งานฟังก์ชัน correct_text
            futures = [executor.submit(correct_text, txt_file) for txt_file in list_of_raw_txts]
            
            # รอให้ทุกฟังก์ชันที่ส่งไปใน future เสร็จสิ้นการทำงาน
            for future in as_completed(futures):
                future.result()  # ดึงผลลัพธ์จาก future (ในที่นี้คือไม่มีการนำผลลัพธ์ไปใช้ต่อ)
    else:
        with ThreadPoolExecutor(max_workers=args.num_proc) as executor:
            # สร้าง futures สำหรับแต่ละไฟล์ข้อความในรายการ โดยเรียกใช้งานฟังก์ชัน correct_text
            futures = [executor.submit(correct_text_with_llm, txt_file) for txt_file in txt_files]
            for future in as_completed(futures):
                future.result()  # ดึงผลลัพธ์จาก future (ในที่นี้คือไม่มีการนำผลลัพธ์ไปใช้ต่อ)
