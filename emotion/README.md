# Emotion & Sentiment Analysis Dataset — Demo Data

Synthetic dataset for **NLP emotion/sentiment classification** on student-related text in **English** and **Bangla**.

---

## File Overview

| # | File | Rows | Labels | Lang |
|---|------|------|--------|------|
| 1 | `emotion_comments_demo.csv` | 3,080 | happy, sad, angry, anxious, neutral, surprised, love (7 × 440) | EN + BN |
| 2 | `sentiment_love_depression_suicide.csv` | 1,500 | fall_in_love, depression, suicide (3 × 500) | EN + BN |
| 3 | `suicide_bangla_1000.csv` | 1,000 | suicide | BN only |
| 4 | `extreme_depression.csv` | 800 | extreme_depression | EN + BN |
| 5 | `extreme_love.csv` | 800 | extreme_love | EN + BN |
| 6 | `extreme_anxiety.csv` | 800 | extreme_anxiety | EN + BN |
| 7 | `work_pressure.csv` | 800 | work_pressure | EN + BN |
| 8 | `academic_pressure.csv` | 800 | academic_pressure | EN + BN |
| 9 | `relationship_issues.csv` | 800 | relationship_issues | EN + BN |
| 10 | `cgpa_money_issues.csv` | 800 | cgpa_money_issues | EN + BN |

---

## Dataset Summary

| Metric | Count |
|--------|-------|
| Total files | 10 |
| Total data rows | **11,189** |
| Unique labels | 14 |
| Languages | English, Bangla |

## Label Distribution

**Label → Total rows (EN / BN):**

| Label | Total | English | Bangla |
|-------|-------|---------|--------|
| happy | 440 | 220 | 220 |
| sad | 440 | 220 | 220 |
| angry | 440 | 220 | 220 |
| anxious | 440 | 220 | 220 |
| neutral | 440 | 220 | 220 |
| surprised | 440 | 220 | 220 |
| love | 440 | 220 | 220 |
| fall_in_love | 500 | 250 | 250 |
| depression | 500 | 250 | 250 |
| suicide | 1,500 | 250 | 1,250 |
| extreme_depression | 800 | 400 | 400 |
| extreme_love | 800 | 400 | 400 |
| extreme_anxiety | 800 | 400 | 400 |
| work_pressure | 800 | 400 | 400 |
| academic_pressure | 800 | 400 | 400 |
| relationship_issues | 800 | 400 | 400 |
| cgpa_money_issues | 800 | 400 | 400 |

---

## Column Schema

All files follow the same format:

```
label      — sentiment/emotion class (string)
language   — "english" or "bangla"      (string)
comment    — the text                    (string)
```

## Notes

- **This is synthetic demo data** for prototyping NLP pipelines. Not for production or clinical use.
- Designed for student-related mental health & emotion detection research.
- Balanced class distribution (equal EN/BN split within each file).
- UTF-8 encoded, comma-separated.
