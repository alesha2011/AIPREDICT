import os

file_path = r"c:\Users\Алексей\Desktop\обучение\predictive-maintenance\frontend\src\pages\Dashboard.tsx"

# The same content as before, but writing with utf-8-sig
with open(file_path, "rb") as f:
    content = f.read().decode("utf-8")

with open(file_path, "w", encoding="utf-8-sig") as f:
    f.write(content)

print("Successfully updated Dashboard.tsx with BOM")
