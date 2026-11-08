import re

text = "Action: search[user nama]"

# Pola regex: Cari kata setelah 'Action: ', ambil nama tool dan isi di dalam kurung siku []
pola = r"Action:\s*([a-zA-Z0-9_]+)\[(.*?)\]"

match = re.search(pola, text)
print(match)
if match:
    tool_name = match.group(1) # Hasil: 'search'
    tool_arg = match.group(2)  # Hasil: 'monas jakarta'
    print(f"Tool: {tool_name}, Argumen: {tool_arg}")
