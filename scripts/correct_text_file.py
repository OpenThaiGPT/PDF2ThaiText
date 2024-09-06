import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pdf2thaitext.correct_text import correct_text

if __name__ == "__main__":
    """
    สคริปต์นี้ใช้ในการอ่านไฟล์ข้อความที่ถูกเก็บไว้ในโฟลเดอร์ที่กำหนด และดำเนินการแก้ไขข้อความ
    โดยใช้ฟังก์ชัน correct_text และทำงานแบบขนานเพื่อเพิ่มประสิทธิภาพในการประมวลผล
    """
    
    path_to_output = "../raw_txt_output/"  # เส้นทางไปยังโฟลเดอร์ที่เก็บไฟล์ข้อความที่ยังไม่ได้แก้ไข
    list_of_name = os.listdir(path_to_output)  # ดึงรายการชื่อไฟล์ทั้งหมดในโฟลเดอร์ที่กำหนด
    list_of_raw_txts = [f"{path_to_output}{txt_file}" for txt_file in list_of_name]  # สร้างรายการเส้นทางไฟล์ข้อความทั้งหมด
    
    # ใช้ ThreadPoolExecutor เพื่อดำเนินการฟังก์ชัน correct_text แบบขนาน
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        # สร้าง futures สำหรับแต่ละไฟล์ข้อความในรายการ โดยเรียกใช้งานฟังก์ชัน correct_text
        futures = [executor.submit(correct_text, txt_file) for txt_file in list_of_raw_txts]
        
        # รอให้ทุกฟังก์ชันที่ส่งไปใน future เสร็จสิ้นการทำงาน
        for future in as_completed(futures):
            future.result()  # ดึงผลลัพธ์จาก future (ในที่นี้คือไม่มีการนำผลลัพธ์ไปใช้ต่อ)
