# AGENTS.md — Multi-Site BD Review Scraper

## Quick start
```bash
source venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium

# Add URLs to daraz/urls.txt and/or rokomari/urls.txt, then:
./run_all.sh                     # both sites (skips already-scraped URLs)
./run_all.sh --force             # re-scrape everything
./run_all.sh daraz               # only Daraz
./run_all.sh --visible           # show browser for debugging
./run_all.sh --install           # first-time: create venv + install deps + playwright
```

Or run a single scraper directly:
```bash
python daraz/scrape.py
python rokomari/scrape.py
```

## Commands
- `./run_all.sh --force` (or `--rescrape`) → sets `SCRAPE_FORCE=1`
- `./run_all.sh --visible` → patches the scraper's `HEADLESS = False` via sed
- `SCRAPE_FORCE=1 python daraz/scrape.py` — bypass CSV dedup per-URL skip

## Configuration (top of each `scrape.py`)
- `HEADLESS = True` — `False` to watch the browser
- `WAIT_TIME = 1` — seconds between actions
- `MAX_PAGES_PER_PRODUCT` — Daraz=10, Rokomari=20 (different defaults)
- `INTER_URL_DELAY = 0.5` — delay between different product URLs
- `SCRAPE_FORCE=1` env var — re-scrape already-scraped URLs

## CSS selectors are brittle
When reviews stop being found, inspect (F12) and update:
- **Daraz** (`daraz/scrape.py`): container `div.item`, text `div.content`, rating `div.star svg`, next `button.next-pagination-item.next`
- **Rokomari** (`rokomari/scrape.py`): fallback selector lists at top of file — add new matches to each list

## Architecture notes
- Scrapers import `_common.py` via `sys.path.insert(0, ...)` from their subdirectory — replicating this is required for new scrapers
- Browser launched with stealth args: `--disable-blink-features=AutomationControlled` and `--lang=bn-BD`
- Dataset CSVs use **UTF-8 BOM** encoding (`utf-8-sig`)

## Dedup
- Existing CSV rows are read by `text` column; new rows with duplicate `text` are skipped
- In-memory dedup per product across pagination pages (detects stale "Next" clicks via `seen_texts` set)
