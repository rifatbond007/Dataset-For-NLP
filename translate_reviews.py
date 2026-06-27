import csv
import re
import sys
import os
from deep_translator import GoogleTranslator

BANGLA_UNICODE_RANGE = re.compile(r'[\u0980-\u09FF]')
LATIN_CHARS = re.compile(r'[a-zA-Z]')

def has_bangla(text):
    return bool(BANGLA_UNICODE_RANGE.search(text))

def is_primarily_english(text):
    text = text.strip()
    if not text:
        return False
    if has_bangla(text):
        return False
    latin_count = len(LATIN_CHARS.findall(text))
    total_chars = len([c for c in text if not c.isspace()])
    if total_chars == 0:
        return False
    return latin_count / total_chars > 0.5

def translate_to_bangla(text, retries=3):
    for attempt in range(retries):
        try:
            translated = GoogleTranslator(source='en', target='bn').translate(text)
            if translated:
                return translated
        except Exception as e:
            if attempt < retries - 1:
                import time
                time.sleep(2)
            else:
                print(f"  Translation failed after {retries} attempts: {e}", file=sys.stderr)
    return text

def process_csv(input_path, output_path):
    rows = []
    total = 0
    translated = 0
    skipped = 0

    with open(input_path, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows.append(header)

        for row in reader:
            if not row or not row[0].strip():
                rows.append(row)
                continue

            total += 1
            original_text = row[0]
            text_only = original_text.split('Color Family:')[0].split('Color Family:')[0].split('কালার_ফ্যামিলি:')[0].split('Multi Verient:')[0].split('exchange:')[0].split('Size:')[0].strip()

            if is_primarily_english(text_only):
                print(f"  Translating [{total}]: {text_only[:80]}...")
                bangla_text = translate_to_bangla(text_only)
                if bangla_text and bangla_text != text_only:
                    row[0] = original_text.replace(text_only, bangla_text)
                    translated += 1
                    print(f"    -> {bangla_text[:80]}...")
                else:
                    skipped += 1
            else:
                skipped += 1

            rows.append(row)

    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerows(rows)

    print(f"\nProcessed {input_path}")
    print(f"  Total reviews: {total}")
    print(f"  Translated: {translated}")
    print(f"  Skipped (already Bangla or not English): {skipped}")
    return translated

if __name__ == '__main__':
    dataset_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dataset')

    files = [
        ('daraz.csv', 'daraz.csv'),
        ('rokomari.csv', 'rokomari.csv'),
    ]

    total_translated = 0
    for input_name, output_name in files:
        input_path = os.path.join(dataset_dir, input_name)
        output_path = os.path.join(dataset_dir, output_name)
        print(f"\n{'='*60}")
        print(f"Processing {input_name}...")
        print(f"{'='*60}")
        t = process_csv(input_path, output_path)
        total_translated += t

    print(f"\n{'='*60}")
    print(f"Done! Total translations: {total_translated}")
