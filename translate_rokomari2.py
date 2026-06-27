import csv
import re
import sys
from deep_translator import GoogleTranslator

BANGLA = re.compile(r'[\u0980-\u09FF]')
LATIN = re.compile(r'[a-zA-Z]')

def is_english(text):
    text = text.strip()
    if not text or BANGLA.search(text):
        return False
    latin = len(LATIN.findall(text))
    total = len([c for c in text if not c.isspace()])
    return total > 0 and latin / total > 0.5

path = '/home/user/Desktop/data scrape/dataset/rokomari.csv'
translator = GoogleTranslator(source='en', target='bn')

# Step 1: Read all rows and collect unique English texts
rows = []
unique_texts = {}
text_map = []

with open(path, 'r', encoding='utf-8-sig', newline='') as f:
    reader = csv.reader(f)
    header = next(reader)
    rows.append(header)
    for row in reader:
        rows.append(row)
        if not row or not row[0].strip():
            text_map.append((None, None))
            continue
        orig = row[0]
        txt = orig
        for sep in ['Color Family:', 'কালার_ফ্যামিলি:', 'Multi Verient:', 'exchange:', 'Size:']:
            txt = txt.split(sep)[0]
        txt = txt.strip()
        if is_english(txt):
            unique_texts[txt] = None
            text_map.append((orig, txt))
        else:
            text_map.append((None, None))

print(f'Total unique English texts to translate: {len(unique_texts)}', flush=True)

# Step 2: Translate all unique texts
cache = {}
for i, txt in enumerate(unique_texts.keys()):
    if txt in cache:
        unique_texts[txt] = cache[txt]
        continue
    print(f'[{i+1}/{len(unique_texts)}] Translating: {txt[:60]}...', flush=True)
    try:
        bt = translator.translate(txt)
        if bt and bt != txt:
            unique_texts[txt] = bt
        else:
            unique_texts[txt] = txt
        cache[txt] = unique_texts[txt]
    except Exception as e:
        print(f'  FAIL: {e}', flush=True)
        unique_texts[txt] = txt
        cache[txt] = txt

print(f'Done translating. Now applying to CSV...', flush=True)

# Step 3: Apply translations to rows
translated = 0
for i, (orig, txt) in enumerate(text_map):
    if orig is not None and txt is not None and unique_texts.get(txt) and unique_texts[txt] != txt:
        rows[i+1][0] = orig.replace(txt, unique_texts[txt], 1)
        translated += 1

# Step 4: Write
with open(path, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f, quoting=csv.QUOTE_ALL)
    w.writerows(rows)

print(f'Done! Translated {translated} rows.')
