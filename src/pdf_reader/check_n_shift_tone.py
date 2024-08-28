import re

import thaispellcheck

def check_tone_vowel_sentence(new):
    tone = [3655, 3656, 3657, 3658, 3659, 3660]
    vowel = [3636, 3637, 3638, 3639, 3640, 3641, 3633]
    
    last_check = thaispellcheck.check(new)
    #print(last_check)
    if "คำผิด" in last_check:
        wrong_word = re.findall(r'<คำผิด>(.*?)</คำผิด>', last_check)
        #print(wrong_word)
        for word in wrong_word:
            word_unicode = [ord(char) for char in word]
            corrected = False
            for i in range(len(word_unicode)):
                if word_unicode[i] in tone or word_unicode[i] in vowel:
                    for j in range(i):
                        if word_unicode[j] not in tone and word_unicode[j] not in vowel:
                            word_unicode[i], word_unicode[j] = word_unicode[j], word_unicode[i]
                                # เช็คคำที่แก้ไขแล้วกับ thaispellcheck
                            new_word = ''.join(chr(c) for c in word_unicode)
                           # print(new_word)
                                # print("PYTHAI:", new_word)
                            check_result = thaispellcheck.check(new_word)
                            if "คำผิด" not in check_result:
                                corrected = True
                                break
                            else:
                                    # ย้ายกลับตำแหน่งเดิม
                                word_unicode[i], word_unicode[j] = word_unicode[j], word_unicode[i]
                    if corrected:
                        break

            if corrected:
                new_word = ''.join(chr(c) for c in word_unicode)
                new = new.replace(word, new_word)
    return new                

def check_tone_vowel_word(word):
    tone = [chr(3655), chr(3656), chr(3657), chr(3658), chr(3659), chr(3660)]
    vowel = [chr(3633), chr(3636), chr(3637), chr(3638), chr(3639), chr(3640), chr(3641)]

    def is_tone_or_vowel(char):
        return char in tone or char in vowel

    # Function to move each marker to all possible positions
    def move_markers(word, marker_indices):
        permutations = set()

        def swap(word_list, i, j):
            word_list[i], word_list[j] = word_list[j], word_list[i]
            return word_list

        # Create all permutations by moving each marker to every possible position
        for i, idx in enumerate(marker_indices):
            for pos in range(1,len(word)):
                if pos != idx and not is_tone_or_vowel(word[pos]):
                    new_word = list(word)
                    new_word.insert(pos, new_word.pop(idx))
                    if "คำผิด" not in thaispellcheck.check("".join(new_word)):
                        permutations.add("".join(new_word))
                        return permutations
        permutations.add("")
        return permutations
    # Find the indices of vowels and tone markers
    marker_indices = [i for i, char in enumerate(word) if is_tone_or_vowel(char)]

    # Generate permutations by moving markers
    all_permutations = set()
    all_permutations.update(move_markers(word, marker_indices))
    if list(all_permutations)[0] == "":
        return word
    else:
        return list(all_permutations)[0] 