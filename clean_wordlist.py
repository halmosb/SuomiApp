# replace_tabs.py
import sys

filepath = sys.argv[1]
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace tab with semicolon
content = content.replace('\t', ';')
content = content.replace('  ', ' ')
content = content.replace('\n\n', '\n')
content = content.replace(' ', ' ')
content = content.replace('­', '')
content = content.replace('’', "'")
content = content.replace('…', "...")
content = content.replace("/", " / ")
content = content.replace("  ", " ")
content = content.replace("–", "-")
content = content.replace('“', '"')
content = content.replace('”', '"')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"File saved.")