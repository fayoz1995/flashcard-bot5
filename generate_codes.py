import json
import os
import random
import string

# Nechta yangi kod yaratilsin
new_codes_count = 1000
code_length = 6
filename = "codes.json"

# Eski kodlar mavjud bo‘lsa — o‘qiymiz
if os.path.exists(filename):
    with open(filename, "r") as f:
        codes = json.load(f)
else:
    codes = {}

# Boshlang‘ich kodlar soni
start_count = len(codes)

# Faqat takrorlanmagan yangi kodlar yaratamiz
while len(codes) < start_count + new_codes_count:
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=code_length))
    if code not in codes:
        codes[code] = {"used": False}

# JSON faylga yozib saqlaymiz
with open(filename, "w") as f:
    json.dump(codes, f, indent=2)

print(f"{new_codes_count} ta yangi kod '{filename}' faylga qo‘shildi.")