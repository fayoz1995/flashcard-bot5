import json

input_file = "codes.json"
output_file = "unused_codes.txt"

# codes.json faylni o‘qiymiz
with open(input_file, "r") as f:
    codes = json.load(f)

# Faqat 'used': false bo‘lganlarni tanlaymiz
unused_codes = [code for code, data in codes.items() if not data.get("used", False)]

# .txt faylga yozamiz
with open(output_file, "w") as f:
    for code in unused_codes:
        f.write(code + "\n")

print(f"{len(unused_codes)} ta kod '{output_file}' faylga chiqarildi.")