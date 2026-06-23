# AGENTS.md — Multi-Site BD Review Scraper

## Project structure
```
_common.py              # shared: launch_browser, clean_text, read_urls, append_reviews_no_dup, get_scraped_urls, scroll_to_reviews
daraz/scrape.py         # Daraz Bangladesh scraper (hardcoded CSS selectors)
daraz/urls.txt          # one URL per line, `#` for comments
rokomari/scrape.py      # Rokomari scraper (fallback CSS selector chains)
rokomari/urls.txt
gorer bazar bd/         # referenced in docs but NOT YET CREATED — no folder, no scraper
dataset/daraz.csv       # output: text, rating, source, product_url (UTF-8 BOM)
dataset/rokomari.csv
run_all.sh              # orchestrator: venv, deps, scraping, summary
```

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
```

Or run a single scraper directly:
```bash
python daraz/scrape.py
python rokomari/scrape.py
```

## Configuration (top of each `scrape.py`)
- `HEADLESS = True` — `False` to watch the browser
- `WAIT_TIME = 1` — seconds between actions
- `MAX_PAGES_PER_PRODUCT = 3` — max review pages per product (lower = faster)
- `SCRAPE_FORCE=1` env var — bypass already-scraped check

## CSS selectors are brittle
When reviews stop being found, inspect (F12) and update:
- **Daraz** (`daraz/scrape.py:72-94`): container `div.item`, text `div.content`, rating `div.star svg`, next `button.next-pagination-item.next`
- **Rokomari** (`rokomari/scrape.py:58-82`): fallback selector lists — add new matching selectors to the top of each list

## Dedup
- Existing CSV rows are read; new rows with identical `text` are skipped
- In-memory dedup per product across pagination pages (detects stale "Next" clicks via `seen_texts` set)

## Notes
- Folder name `gorer bazar bd` has spaces — always quote paths
- Scripts have Bengali comments/docstrings
- `run_all.sh` creates venv automatically if missing (with `--install`)
- Dataset summary printed after `run_all.sh`: totals, source breakdown, new reviews added
