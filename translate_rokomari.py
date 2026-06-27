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
cache = {}
rows = []
total = 0
translated = 0
skipped = 0

with open(path, 'r', encoding='utf-8-sig', newline='') as f:
    reader = csv.reader(f)
    header = next(reader)
    rows.append(header)
    for row in reader:
        total += 1
        if not row or not row[0].strip():
            rows.append(row)
            continue

        orig = row[0]
        txt = orig
        for sep in ['Color Family:', 'কালার_ফ্যামিলি:', 'Multi Verient:', 'exchange:', 'Size:']:
            txt = txt.split(sep)[0]
        txt = txt.strip()

        if txt in cache:
            bt = cache[txt]
            if bt and bt != txt:
                row[0] = orig.replace(txt, bt, 1)
                translated += 1
            else:
                skipped += 1
            rows.append(row)
            continue

        if is_english(txt):
            print(f'[{total}] {txt[:60]}...', flush=True)
            try:
                bt = translator.translate(txt)
                if bt and bt != txt:
                    row[0] = orig.replace(txt, bt, 1)
                    translated += 1
                else:
                    skipped += 1
                cache[txt] = bt
            except Exception as e:
                print(f'  FAIL: {e}', flush=True)
                skipped += 1
                cache[txt] = txt
        else:
            skipped += 1
            cache[txt] = txt
        rows.append(row)

with open(path, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f, quoting=csv.QUOTE_ALL)
    w.writerows(rows)

print(f'\nDone: total={total}, translated={translated}, skipped={skipped}')
