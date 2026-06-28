# AGENTS.md

## What this repo is

190k synthetic text samples (English + Bangla) for emotion/sentiment/mental-health NLP research. No code, no build system, no tests — just 10 CSV files and a README.

## Structure

- **10 CSV files** in root, all with the same 3-column schema: `label,language,comment`
- **emotion_comments_demo.csv** (70k rows, 7 labels) is the core dataset
- **sentiment_love_depression_suicide.csv** (40k rows, 3 labels)
- **suicide_bangla_1000.csv** (10k rows, 1 label — BN only)
- **6 small files** (800 rows each) for student-specific stressors (academic pressure, work pressure, relationships, CGPA/money, extreme depression/anxiety/love)

## Dataset facts

| Attribute | Value |
|-----------|-------|
| Total samples | 190,000 |
| Languages | English (90k), Bangla (100k) |
| Unique labels | 17 |
| Encoding | UTF-8 |
| Balanced per file (equal EN/BN split except suicide_bangla_1000) | |

## Schema

```
label,language,comment
happy,english,"I am so happy today!"
suicide,bangla,"আমার জীবন শেষ করতে চাই"
```

Columns: `label` (str), `language` (str, `"english"` or `"bangla"`), `comment` (str).

## Key notes

- **Synthetic data** — not real human utterances. For research/prototyping only, not clinical use.
- No PII present.
- Suicide-related content included for academic research.
- No code, scripts, notebooks, or config files exist in this repo.
- Git tracks only the CSV data + README + AGENTS.md.
