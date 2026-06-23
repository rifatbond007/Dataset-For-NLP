"""
Common helpers (shared utilities for the site scraper scripts)
============================================================
This module contains helper functions shared by the site scrapers
(daraz, rokomari, gorer bazar bd) so that code is not duplicated:
    - launching the browser
    - cleaning text
    - scrolling to trigger lazy-loaded review sections
    - reading urls.txt
    - tracking already-scraped URLs
    - appending reviews to CSV while skipping duplicates (UTF-8 BOM)
"""

import sys
import csv
import time
import re
from pathlib import Path
from playwright.sync_api import sync_playwright


# Project root (the folder this file lives in)
ROOT = Path(__file__).resolve().parent


def launch_browser(pw, headless=True):
    """
    Launch a Playwright Chromium browser (same args as the original
    Daraz scraper). Returns: (browser, page)
    """
    browser = pw.chromium.launch(
        headless=headless,
        args=[
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--window-size=1920,1080",
            "--disable-blink-features=AutomationControlled",
            "--lang=bn-BD",
        ],
    )
    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        ),
        viewport={"width": 1920, "height": 1080},
    )
    page = context.new_page()
    return browser, page


def clean_text(text):
    """Collapse multiple spaces/newlines and strip the result."""
    return re.sub(r"\s+", " ", text or "").strip()


def scroll_to_reviews(page, wait_time=3):
    """
    Scroll the page to 60% of its height to trigger lazy-loaded
    review sections, then wait briefly.
    """
    try:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.6);")
    except Exception:
        pass
    time.sleep(wait_time)


def polite_delay(seconds=2):
    """
    Short pause between URLs to reduce load on the target site.
    Use when scraping multiple URLs in a row.
    """
    time.sleep(seconds)


def get_first_review_signature(page):
    """
    Capture a short text 'fingerprint' of the first review on the
    current page. Used to detect that a 'Next' click actually
    changed the page (so the next scrape doesn't re-read the
    same page). Returns "" if no review is found.
    """
    selectors = [
        "div.item div.content",
        "div.item div.item-content",
        ".review-item .review-text",
        ".review-item .review-content",
        ".review",
        "div.reviewItem",
    ]
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            if loc.count() > 0:
                txt = clean_text(loc.text_content() or "")
                if txt:
                    return txt[:200]
        except Exception:
            continue
    return ""


def read_urls(urls_file: Path) -> list:
    """
    Read the URL list from urls.txt.
    - blank lines are ignored
    - lines starting with '#' are treated as comments and skipped
    """
    if not urls_file.exists():
        return []
    with open(urls_file, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]


def get_scraped_urls(csv_path: Path) -> set:
    """
    Return the set of URLs already present in the CSV (from the
    'product_url' column). Use this before scraping to know which
    URLs to skip.

    - Returns an empty set if the CSV does not exist
    - Reads with UTF-8 BOM (same as append_reviews_no_dup)
    - Skips blank / whitespace-only URLs
    """
    if not csv_path.exists():
        return set()
    urls: set = set()
    try:
        with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                u = (row.get("product_url") or "").strip()
                if u:
                    urls.add(u)
    except Exception:
        # If the CSV is corrupt or header mismatches, return an empty
        # set as a safe default (everything will be scraped fresh).
        return set()
    return urls


def append_reviews_no_dup(csv_path: Path, rows: list, fieldnames: list):
    """
    Append new reviews to the CSV, skipping any whose 'text' is already
    present in the file. On first run, the file is created and the
    header is written.

    Returns: (written_count, skipped_count)
    """
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    existing_texts = set()
    is_new_file = not csv_path.exists()

    if not is_new_file:
        with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("text"):
                    existing_texts.add(row["text"])

    fresh_rows = [r for r in rows if r.get("text") and r["text"] not in existing_texts]
    skipped = len(rows) - len(fresh_rows)

    if not fresh_rows and not is_new_file:
        return 0, skipped

    write_header = is_new_file
    with open(csv_path, "a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerows(fresh_rows)

    return len(fresh_rows), skipped
