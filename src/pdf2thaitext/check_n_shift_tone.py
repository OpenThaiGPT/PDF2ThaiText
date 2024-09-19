import re
import thaispellcheck

def check_tone_vowel_sentence(new):
    """
    ฟังก์ชันนี้ใช้สำหรับตรวจสอบและแก้ไขคำในประโยคให้มีการจัดเรียงสระและวรรณยุกต์ให้ถูกต้อง
    
    Args:
        new (str): ประโยคที่ต้องการตรวจสอบและแก้ไข
        
    Returns:
        str: ประโยคที่ได้รับการตรวจสอบและแก้ไขแล้ว
    """
    
    tone = [3655, 3656, 3657, 3658, 3659, 3660]  # รายการวรรณยุกต์ใน Unicode
    vowel = [3636, 3637, 3638, 3639, 3640, 3641, 3633]  # รายการสระใน Unicode
    
    last_check = thaispellcheck.check(new)  # ตรวจสอบคำในประโยค
    if "คำผิด" in last_check:
        wrong_word = re.findall(r'<คำผิด>(.*?)</คำผิด>', last_check)  # หาและเก็บคำที่ผิดไว้ในรายการ
        for word in wrong_word:
            word_unicode = [ord(char) for char in word]  # แปลงคำเป็นรายการของ Unicode
            corrected = False
            for i in range(len(word_unicode)):
                if word_unicode[i] in tone or word_unicode[i] in vowel:
                    for j in range(i):
                        if word_unicode[j] not in tone and word_unicode[j] not in vowel:
                            word_unicode[i], word_unicode[j] = word_unicode[j], word_unicode[i]  # สลับตำแหน่งของตัวอักษร
                            new_word = ''.join(chr(c) for c in word_unicode)  # แปลงกลับเป็นคำ
                            check_result = thaispellcheck.check(new_word)  # ตรวจสอบคำที่แก้ไขแล้ว
                            if "คำผิด" not in check_result:
                                corrected = True
                                break
                            else:
                                word_unicode[i], word_unicode[j] = word_unicode[j], word_unicode[i]  # ย้ายกลับตำแหน่งเดิมถ้าผลลัพธ์ยังผิดอยู่
                    if corrected:
                        break

            if corrected:
                new_word = ''.join(chr(c) for c in word_unicode)
                new = new.replace(word, new_word)  # แทนที่คำผิดในประโยคด้วยคำที่ถูกต้อง
    return new                

def check_tone_vowel_word(word):
    """
    ฟังก์ชันนี้ใช้สำหรับตรวจสอบและแก้ไขคำให้มีการจัดเรียงสระและวรรณยุกต์ให้ถูกต้อง
    
    Args:
        word (str): คำที่ต้องการตรวจสอบและแก้ไข
        
    Returns:
        str: คำที่ได้รับการตรวจสอบและแก้ไขแล้ว
    """
    
    tone = [chr(3655), chr(3656), chr(3657), chr(3658), chr(3659), chr(3660)]  # รายการวรรณยุกต์ใน Unicode
    vowel = [chr(3633), chr(3636), chr(3637), chr(3638), chr(3639), chr(3640), chr(3641)]  # รายการสระใน Unicode

    def is_tone_or_vowel(char):
        """
        ฟังก์ชันย่อยนี้ใช้สำหรับตรวจสอบว่าตัวอักษรเป็นวรรณยุกต์หรือสระหรือไม่
        
        Args:
            char (str): ตัวอักษรที่ต้องการตรวจสอบ
            
        Returns:
            bool: คืนค่า True หากเป็นวรรณยุกต์หรือสระ มิฉะนั้น คืนค่า False
        """
        return char in tone or char in vowel

    def move_markers(word, marker_indices):
        """
        ฟังก์ชันย่อยนี้ใช้สำหรับเคลื่อนย้ายวรรณยุกต์และสระในคำไปยังตำแหน่งที่เป็นไปได้ทั้งหมด
        
        Args:
            word (str): คำที่ต้องการเคลื่อนย้ายวรรณยุกต์และสระ
            marker_indices (list): รายการตำแหน่งของวรรณยุกต์และสระในคำ
            
        Returns:`
            set: เซ็ตของคำที่มีการเคลื่อนย้ายวรรณยุกต์และสระ
        """
        permutations = set()

        # สร้างทุกความเป็นไปได้โดยการเคลื่อนย้ายแต่ละเครื่องหมายไปยังทุกตำแหน่งที่เป็นไปได้
        for i, idx in enumerate(marker_indices):
            for pos in range(1, len(word)):
                if pos != idx and not is_tone_or_vowel(word[pos]):
                    new_word = list(word)
                    new_word.insert(pos, new_word.pop(idx))  # เคลื่อนย้ายเครื่องหมาย
                    if "คำผิด" not in thaispellcheck.check("".join(new_word)):
                        permutations.add("".join(new_word))
                        return permutations
        permutations.add("")
        return permutations
    
    marker_indices = [i for i, char in enumerate(word) if is_tone_or_vowel(char)]  # หาตำแหน่งของวรรณยุกต์และสระ

    all_permutations = set()
    all_permutations.update(move_markers(word, marker_indices))  # สร้างคำที่เป็นไปได้โดยการเคลื่อนย้ายเครื่องหมาย
    if list(all_permutations)[0] == "":
        return word  # คืนค่าคำเดิมหากไม่พบคำที่ถูกต้อง
    else:
        return list(all_permutations)[0]  # คืนค่าคำที่ถูกต้องคำแรกในเซ็ต
