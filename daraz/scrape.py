"""
Daraz Bangladesh — Product Review Scraper
==========================================
This script collects customer reviews from Daraz product pages and
appends them to dataset/daraz.csv (skipping duplicates).

Before running:
1. Install packages from requirements.txt: pip install -r requirements.txt
2. Install the browser: python -m playwright install chromium
3. Paste one Daraz product URL per line into urls.txt
4. Run with: python scrape.py

Important notes:
- Daraz's HTML structure can change over time, so you may need to
  verify/update the CSS selectors by inspecting the page (F12) in a
  real browser.
- Set HEADLESS = False to watch the browser while it runs (useful for
  debugging).
- A small delay is inserted between requests to keep load on the
  site reasonable.
- Re-running with the same URLs will not add duplicate reviews.
"""

import sys
import os
import time
from pathlib import Path

# Add project root to sys.path so we can import _common.py
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _common import (
    launch_browser,
    clean_text,
    read_urls,
    append_reviews_no_dup,
    get_scraped_urls,
    get_first_review_signature,
    scroll_to_reviews,
    polite_delay,
    ROOT,
)
from playwright.sync_api import sync_playwright


# ===================== CONFIG (edit here if needed) =====================

HEADLESS = True                 # True = hidden browser, False = visible
WAIT_TIME = 1                   # Seconds to wait after each action
MAX_PAGES_PER_PRODUCT = 10       # Max review pages to scrape per product
INTER_URL_DELAY = 0.5           # Seconds to wait between URLs
SOURCE_NAME = "Daraz"           # Value written to the CSV 'source' column

URLS_FILE = Path(__file__).resolve().parent / "urls.txt"
OUTPUT_CSV = ROOT / "dataset" / "daraz.csv"
CSV_FIELDS = ["text", "rating", "source", "product_url"]


# ===================== SCRAPING FUNCTIONS =====================

def scrape_reviews_from_page(page):
    """
    Collect all reviews currently visible on the page.

    NOTE: The CSS selectors below may need to be updated to match
    Daraz's current HTML. Open the page in a browser, press F12,
    right-click a review and choose 'Inspect' to find the actual
    class/element names, then replace the selectors below.
    """
    reviews = []

    try:
        page.wait_for_selector("div.item", timeout=10000)
    except Exception:
        return reviews

    review_items = page.locator("div.item").all()

    for item in review_items:
        review_text = ""
        try:
            text_el = item.locator("div.content, div.item-content").first
            review_text = clean_text(text_el.text_content() or "")
        except Exception:
            pass

        rating = ""
        try:
            rating_el = item.locator("div.star svg, div.rating-stars").first
            rating = rating_el.get_attribute("aria-label") or rating_el.get_attribute("title") or ""
        except Exception:
            pass

        if review_text:
            reviews.append({"text": review_text, "rating": rating})

    return reviews


def go_to_next_page(page):
    """Go to the next review page. Returns False if 'Next' is missing or disabled."""
    try:
        next_btn = page.locator("button.next-pagination-item.next").first
        if not next_btn.is_visible(timeout=5000):
            return False
        class_attr = next_btn.get_attribute("class") or ""
        if "disabled" in class_attr:
            return False
        next_btn.scroll_into_view_if_needed()
        time.sleep(WAIT_TIME)
        next_btn.click()
        time.sleep(WAIT_TIME)
        return True
    except Exception:
        return False


# ===================== MAIN =====================

def main():
    urls = read_urls(URLS_FILE)
    if not urls:
        print(f"[WARN] No URLs found in urls.txt ({URLS_FILE})")
        print("       Add one Daraz URL per line in urls.txt.")
        return

    # FORCE: when SCRAPE_FORCE=1 is set, already-scraped URLs are re-scraped too.
    force = os.environ.get("SCRAPE_FORCE", "").lower() in ("1", "true", "yes")

    if force:
        print(f"[INFO] Found {len(urls)} URL(s) (FORCE mode — all will be scraped).")
    else:
        already = get_scraped_urls(OUTPUT_CSV)
        if already:
            skipped_urls = [u for u in urls if u in already]
            new_urls = [u for u in urls if u not in already]
            for u in skipped_urls:
                print(f"  [SKIP] Already scraped: {u}")
            if not new_urls:
                print(f"[INFO] All {len(urls)} URL(s) in urls.txt are already scraped. Nothing to do.")
                print("       Force re-scrape: SCRAPE_FORCE=1 python scrape.py")
                return
            print(f"[INFO] Found {len(urls)} URL(s) — {len(skipped_urls)} skipped, {len(new_urls)} new to scrape.")
            urls = new_urls
        else:
            print(f"[INFO] Found {len(urls)} URL(s).")

    all_reviews = []
    per_url_counts = []
    with sync_playwright() as pw:
        browser, page = launch_browser(pw, headless=HEADLESS)
        try:
            for idx, url in enumerate(urls, start=1):
                print(f"\n[INFO] ({idx}/{len(urls)}) Processing: {url}")
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=30000)
                except Exception as e:
                    print(f"  [WARN] Failed to load page: {e}")
                    per_url_counts.append((url, 0, "load_failed"))
                    continue
                time.sleep(WAIT_TIME)

                scroll_to_reviews(page, wait_time=WAIT_TIME)

                url_reviews = []
                seen_texts: set = set()  # in-memory dedup across pages of this URL
                consecutive_empty = 0
                for pg in range(MAX_PAGES_PER_PRODUCT):
                    print(f"  [INFO] Reading review page {pg + 1}/{MAX_PAGES_PER_PRODUCT}...")
                    reviews = scrape_reviews_from_page(page)

                    # Stamp metadata
                    for r in reviews:
                        r["source"] = SOURCE_NAME
                        r["product_url"] = url

                    # Drop reviews whose text was already collected from
                    # an earlier page on this same URL (e.g. when 'Next'
                    # didn't actually change the page).
                    new_reviews = []
                    for r in reviews:
                        t = r.get("text", "")
                        if t and t not in seen_texts:
                            seen_texts.add(t)
                            new_reviews.append(r)

                    url_reviews.extend(new_reviews)
                    dupes = len(reviews) - len(new_reviews)
                    print(f"  [INFO] Found {len(reviews)} review(s) on this page "
                          f"({len(new_reviews)} new, {dupes} duplicate(s) skipped)")

                    if len(reviews) == 0:
                        consecutive_empty += 1
                        if consecutive_empty >= 2:
                            # Two empty pages in a row = definitely no more
                            print("  [INFO] Two empty pages in a row, finished this product.")
                            break
                        print("  [WARN] No reviews found. Will try next page once more.")
                    else:
                        consecutive_empty = 0

                    # Don't try to click 'Next' on the last allowed page
                    if pg + 1 >= MAX_PAGES_PER_PRODUCT:
                        print("  [INFO] Reached MAX_PAGES_PER_PRODUCT, finished this product.")
                        break

                    if not go_to_next_page(page):
                        print("  [INFO] No next page, finished this product.")
                        break

                all_reviews.extend(url_reviews)
                per_url_counts.append((url, len(url_reviews), "ok"))
                print(f"  [INFO] Total {len(url_reviews)} review(s) collected from this URL.")

                # Small pause between URLs (skip after the last one)
                if idx < len(urls):
                    polite_delay(INTER_URL_DELAY)
        finally:
            browser.close()

    # Per-URL summary printed to the console
    print("\n[INFO] Per-URL summary:")
    for url, count, status in per_url_counts:
        print(f"  - {count:>3} reviews  [{status}]  {url}")

    if all_reviews:
        written, skipped = append_reviews_no_dup(OUTPUT_CSV, all_reviews, CSV_FIELDS)
        print(f"\n[DONE] {written} new review(s) saved to '{OUTPUT_CSV}' ({skipped} duplicate(s) skipped).")
    else:
        print("\n[FAIL] No reviews were collected.")
        print("       Possible causes:")
        print("       1. urls.txt contains wrong/sample links.")
        print("       2. CSS selectors don't match the current Daraz page (inspect and update).")
        print("       3. The page is taking too long to load (try increasing WAIT_TIME).")


if __name__ == "__main__":
    main()