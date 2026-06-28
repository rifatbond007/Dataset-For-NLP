# Multilingual Emotion & Sentiment Dataset for NLP Research

A synthetically generated, labeled dataset of **11,189 text samples** in **English** and **Bangla (Bengali)**, designed for emotion classification, sentiment analysis, and mental health risk detection in student-related contexts.

---

## Contents

- [Dataset Overview](#dataset-overview)
- [File Descriptions](#file-descriptions)
- [Label Distribution](#label-distribution)
- [Schema](#schema)
- [Use Cases](#use-cases)
- [Limitations & Ethics](#limitations--ethics)

---

## Dataset Overview

| Attribute | Details |
|-----------|---------|
| **Total samples** | 11,189 |
| **Languages** | English (5,910) · Bangla (5,279) |
| **Unique labels** | 14 |
| **Files** | 10 CSV files |
| **Encoding** | UTF-8 |
| **Format** | Comma-separated values (CSV) |
| **Class balance** | Balanced per file (equal EN/BN split) |

---

## File Descriptions

### Core Emotion Dataset

| # | File | Rows | Labels | Languages |
|---|------|------|--------|-----------|
| 1 | `emotion_comments_demo.csv` | 3,080 | happy · sad · angry · anxious · neutral · surprised · love | EN · BN |

### Targeted Sentiment Datasets

| # | File | Rows | Labels | Languages |
|---|------|------|--------|-----------|
| 2 | `sentiment_love_depression_suicide.csv` | 1,500 | fall_in_love · depression · suicide | EN · BN |
| 3 | `suicide_bangla_1000.csv` | 1,000 | suicide | BN |

### Student-Specific Stressors

| # | File | Rows | Domain | Languages |
|---|------|------|--------|-----------|
| 4 | `extreme_depression.csv` | 800 | Clinical depression | EN · BN |
| 5 | `extreme_love.csv` | 800 | Intense romantic emotions | EN · BN |
| 6 | `extreme_anxiety.csv` | 800 | Anxiety & panic | EN · BN |
| 7 | `work_pressure.csv` | 800 | Workplace stress | EN · BN |
| 8 | `academic_pressure.csv` | 800 | Academic stress & exams | EN · BN |
| 9 | `relationship_issues.csv` | 800 | Interpersonal conflict | EN · BN |
| 10 | `cgpa_money_issues.csv` | 800 | Financial & grade anxiety | EN · BN |

---

## Label Distribution

| Label | Total | English | Bangla |
|-------|------:|--------:|-------:|
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

## Schema

All 10 CSV files share an identical three-column structure:

```csv
label,language,comment
happy,english,"I am so happy today!"
suicide,bangla,"আমি আমার জীবন শেষ করতে চাই"
```

| Column | Type | Description |
|--------|------|-------------|
| `label` | `str` | Emotion or sentiment class label |
| `language` | `str` | Language of the text (`"english"` or `"bangla"`) |
| `comment` | `str` | The natural language text sample |

---

## Use Cases

- **Emotion classification** — multi-class text classification (7–14 classes)
- **Cross-lingual NLP** — train on English, evaluate on Bangla (or vice versa)
- **Mental health monitoring** — suicide risk, depression, and anxiety detection
- **Student well-being research** — academic pressure, relationship issues, financial stress
- **Sentiment analysis** — positive (love/happy) vs. negative (sad/suicide/depression) vs. neutral

---

## Limitations & Ethics

> ⚠️ **Synthetic data.** All samples are programmatically generated and do not represent real individuals, utterances, or experiences. This dataset is intended **for research and prototyping only**.

- **Not for clinical use.** Do not use this data for real-world mental health screening, diagnosis, or intervention without rigorous validation on real-world data.
- **Risk of bias.** Synthetic data may not capture the nuance, severity, or linguistic patterns of genuine distress.
- **Privacy safe.** No personally identifiable information (PII) is present.
- **Suicide-related content** is included for academic research on automated suicide risk detection. Handle with appropriate care and institutional oversight.

---

## Citation

If you use this dataset in your research, please cite:

```bibtex
@misc{emotion-dataset-2026,
  author = {Abdullah Al Rifat},
  title  = {Multilingual Emotion \& Sentiment Dataset for NLP Research},
  year   = {2026},
  url    = {https://github.com/rifatbond007/Dataset-For-NLP}
}
```

---

<p align="center"><b>Built for research · Not for production</b></p>
