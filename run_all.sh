#!/usr/bin/env bash
# =============================================================================
# run_all.sh — One-shot scraper for all sites
# =============================================================================
# Usage:
#   chmod +x run_all.sh        # one-time only (first run)
#   ./run_all.sh               # run all sites
#   ./run_all.sh daraz         # only Daraz
#   ./run_all.sh rokomari      # only Rokomari
#   ./run_all.sh --visible     # show the browser window (HEADLESS=False)
#   ./run_all.sh --force       # re-scrape already-scraped URLs as well
#   ./run_all.sh --install     # first-time: create venv + install deps + playwright
#
# What it does:
#   1. Activates the venv (or creates it via --install if missing)
#   2. Skips URLs in urls.txt that are already in dataset/<site>.csv
#   3. Scrapes only the new URLs from each site
#   4. Prints a summary of the dataset/ folder at the end
# =============================================================================

set -euo pipefail

# Color codes for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Project root (the folder this script lives in)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ---------- Defaults ----------
SITES=("daraz" "rokomari")
DO_INSTALL=false
HEADLESS_OVERRIDE=""
FORCE_ENV=""   # When set to "SCRAPE_FORCE=1", already-scraped URLs are re-scraped too

# ---------- Argument parsing ----------
while [[ $# -gt 0 ]]; do
    case "$1" in
        --install)
            DO_INSTALL=true
            shift
            ;;
        --visible)
            HEADLESS_OVERRIDE="HEADLESS = False"
            shift
            ;;
        --headless)
            HEADLESS_OVERRIDE="HEADLESS = True"
            shift
            ;;
        --force|--rescrape)
            FORCE_ENV="SCRAPE_FORCE=1"
            shift
            ;;
        daraz|rokomari)
            SITES=("$1")
            shift
            ;;
        -h|--help)
            sed -n '2,17p' "$0"
            exit 0
            ;;
        *)
            echo -e "${RED}[ERROR] Unknown argument: $1${NC}"
            echo "Run '$0 --help' for usage."
            exit 1
            ;;
    esac
done

# ---------- Helper functions ----------
print_header() {
    echo -e "\n${CYAN}============================================================${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}============================================================${NC}"
}

print_ok() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_err() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ---------- Install / setup ----------
ensure_setup() {
    # Check for venv
    if [[ ! -d "venv" ]]; then
        print_warn "venv not found — creating it now..."
        python3 -m venv venv
    fi

    # shellcheck source=/dev/null
    source venv/bin/activate

    # Check for playwright
    if ! python -c "import playwright" 2>/dev/null; then
        print_warn "playwright not installed — installing now..."
        pip install --quiet -r requirements.txt
    fi

    # Check for chromium browser
    if ! python -c "from playwright.sync_api import sync_playwright; sync_playwright().start().chromium.executable_path" 2>/dev/null; then
        print_warn "Installing Playwright Chromium browser (this may take a while)..."
        python -m playwright install chromium
    fi

    print_ok "Setup complete"
}

# ---------- Run one site ----------
# Globals: how many new comments were added per site (NEW_BY_SITE) — shown in summary
# Globals: how many URLs were skipped per site (SKIPPED_BY_SITE) — shown in summary
NEW_BY_SITE=""
SKIPPED_BY_SITE=""

run_site() {
    local site="$1"
    local script="$site/scrape.py"
    local urls_file="$site/urls.txt"

    if [[ ! -f "$script" ]]; then
        print_err "$script not found — skipping"
        return 1
    fi

    # Check if urls.txt is empty
    if [[ ! -s "$urls_file" ]]; then
        print_warn "$urls_file is empty or missing — skipping $site"
        return 0
    fi

    local count
    count=$(grep -cv '^\s*#\|^\s*$' "$urls_file" 2>/dev/null || echo 0)
    if [[ -n "$FORCE_ENV" ]]; then
        print_header "$site — $count URL(s) to scrape (FORCE)"
    else
        print_header "$site — new URLs out of $count will be scraped"
    fi
    echo -e "  Script: $script"
    echo -e "  URLs:   $urls_file"
    echo ""

    # Count rows in the CSV before the run
    local csv_path="dataset/${site}.csv"
    local before_rows=0
    if [[ -f "$csv_path" ]]; then
        before_rows=$(($(wc -l < "$csv_path") - 1))
        [[ $before_rows -lt 0 ]] && before_rows=0
    fi

    # Capture the script output so we can parse the [DONE] line later
    local script_output rc
    if [[ -n "$HEADLESS_OVERRIDE" ]]; then
        local tmp_script
        tmp_script="$(mktemp /tmp/scrape_${site}_XXXXXX.py)"
        sed "s/^HEADLESS = .*/${HEADLESS_OVERRIDE}/" "$script" > "$tmp_script"
        script_output=$(env ${FORCE_ENV:-} python "$tmp_script" 2>&1) || rc=$?; rc=${rc:-0}
        rm -f "$tmp_script"
    else
        script_output=$(env ${FORCE_ENV:-} python "$script" 2>&1) || rc=$?; rc=${rc:-0}
    fi

    # Echo the captured output so the user sees it in the terminal
    echo "$script_output"

    # Parse the new-review count from the [DONE] line, e.g. "[DONE] 7 new review(s) saved..."
    local new_count=0
    local done_line
    done_line=$(echo "$script_output" | grep -E '\[DONE\]' | head -1 || true)
    if [[ -n "$done_line" ]]; then
        # Extract the first number on the line
        new_count=$(echo "$done_line" | grep -oE '[0-9]+' | head -1 || echo 0)
    fi

    # Fallback: count rows before/after if no [DONE] line was found
    if [[ -z "$new_count" || "$new_count" == "0" ]]; then
        local after_rows=0
        if [[ -f "$csv_path" ]]; then
            after_rows=$(($(wc -l < "$csv_path") - 1))
            [[ $after_rows -lt 0 ]] && after_rows=0
        fi
        new_count=$((after_rows - before_rows))
        [[ $new_count -lt 0 ]] && new_count=0
    fi

    # Append to NEW_BY_SITE (shown in the summary)
    if [[ -z "$NEW_BY_SITE" ]]; then
        NEW_BY_SITE="${site}|${new_count}"
    else
        NEW_BY_SITE="${NEW_BY_SITE}
${site}|${new_count}"
    fi

    # Append to SKIPPED_BY_SITE (counted from [SKIP] lines emitted by the Python script)
    local skip_count
    skip_count=$(echo "$script_output" | grep -c '\[SKIP\]' || true)
    if [[ -z "$SKIPPED_BY_SITE" ]]; then
        SKIPPED_BY_SITE="${site}|${skip_count}"
    else
        SKIPPED_BY_SITE="${SKIPPED_BY_SITE}
${site}|${skip_count}"
    fi

    return $rc
}

# ---------- Dataset summary ----------
show_dataset_summary() {
    print_header "dataset/ summary"

    if [[ ! -d "dataset" ]]; then
        print_warn "dataset/ folder does not exist"
        return 0
    fi

    local total_rows=0
    local total_with_rating=0
    local total_chars=0

    # ---------- Table 1: row count per file ----------
    printf "  %-30s %10s %10s %10s\n" "File" "Total" "With rating" "Size"
    printf "  %-30s %10s %10s %10s\n" "----" "-----" "-----------" "----"

    shopt -s nullglob
    for f in dataset/*.csv; do
        local rows
        rows=$(($(wc -l < "$f") - 1))   # subtract header
        [[ $rows -lt 0 ]] && rows=0

        local with_rating
        # Count rows with a non-empty 'rating' column (accurate via Python)
        with_rating=$(python3 - "$f" <<'PYEOF' 2>/dev/null || echo 0
import sys, csv
try:
    with open(sys.argv[1], encoding='utf-8-sig', newline='') as fh:
        r = csv.DictReader(fh)
        n = sum(1 for row in r if (row.get('rating') or '').strip())
    print(n)
except Exception:
    print(0)
PYEOF
)

        local size chars
        size=$(du -h "$f" | cut -f1)
        chars=$(wc -c < "$f")
        total_chars=$((total_chars + chars))

        printf "  %-30s %10d %10s %10s\n" "$(basename "$f")" "$rows" "$with_rating" "$size"
        total_rows=$((total_rows + rows))
        total_with_rating=$((total_with_rating + with_rating))
    done
    shopt -u nullglob

    # ---------- Table 2: breakdown by 'source' column ----------
    echo ""
    printf "  %-20s %10s\n" "source" "comments"
    printf "  %-20s %10s\n" "------" "--------"

    local source_breakdown
    source_breakdown=$(python3 - <<'PYEOF' 2>/dev/null || true
import csv, os
from collections import Counter
c = Counter()
for fn in os.listdir('dataset'):
    if not fn.endswith('.csv'):
        continue
    p = os.path.join('dataset', fn)
    try:
        with open(p, encoding='utf-8-sig', newline='') as fh:
            for row in csv.DictReader(fh):
                src = (row.get('source') or '').strip() or '(unknown)'
                c[src] += 1
    except Exception:
        pass
for k in sorted(c):
    print(f"{k}|{c[k]}")
PYEOF
)

    while IFS='|' read -r src cnt; do
        [[ -z "$src" ]] && continue
        printf "  %-20s %10s\n" "$src" "$cnt"
    done <<< "$source_breakdown"

    # ---------- New reviews added in this run ----------
    if [[ -n "${NEW_BY_SITE:-}" && "$NEW_BY_SITE" != "" ]]; then
        echo ""
        printf "  %-20s %10s\n" "New in this run" "comments"
        printf "  %-20s %10s\n" "--------------" "--------"
        local new_total=0
        while IFS='|' read -r site cnt; do
            [[ -z "$site" ]] && continue
            printf "  %-20s %10s\n" "$site" "$cnt"
            new_total=$((new_total + cnt))
        done <<< "$NEW_BY_SITE"
        printf "  %-20s %10s\n" "Total new" "$new_total"
    fi

    # ---------- URLs skipped in this run ----------
    if [[ -n "${SKIPPED_BY_SITE:-}" && "$SKIPPED_BY_SITE" != "" ]]; then
        echo ""
        printf "  %-20s %10s\n" "Skipped URLs" "count"
        printf "  %-20s %10s\n" "------------" "-----"
        local skip_total=0
        while IFS='|' read -r site cnt; do
            [[ -z "$site" ]] && continue
            printf "  %-20s %10s\n" "$site" "$cnt"
            skip_total=$((skip_total + cnt))
        done <<< "$SKIPPED_BY_SITE"
        printf "  %-20s %10s\n" "Total skipped" "$skip_total"
    fi

    # ---------- Grand totals ----------
    echo ""
    echo "  -----------------------------------------------"
    print_ok "dataset/ total comments: ${total_rows}"
    if [[ $total_with_rating -gt 0 ]]; then
        print_ok "with rating:            ${total_with_rating} (${total_with_rating}/${total_rows} = $(awk -v a=$total_with_rating -v b=$total_rows 'BEGIN{ if(b>0) printf "%.1f", (a*100.0/b); else print "0.0" }')%)"
    fi
    if [[ $total_rows -gt 0 ]]; then
        # Average review length in characters
        local avg_len
        avg_len=$(python3 - <<'PYEOF' 2>/dev/null || echo "0"
import csv, os
total = 0; count = 0
for fn in os.listdir('dataset'):
    if not fn.endswith('.csv'): continue
    p = os.path.join('dataset', fn)
    try:
        with open(p, encoding='utf-8-sig', newline='') as fh:
            for row in csv.DictReader(fh):
                t = (row.get('text') or '').strip()
                if t:
                    total += len(t); count += 1
    except Exception:
        pass
print(int(total / count) if count else 0)
PYEOF
)
        print_ok "average review length:   ${avg_len} characters"
    fi
    echo ""
}

# ---------- Main ----------
main() {
    print_header "Multi-Site BD Review Scraper"
    if [[ -n "$FORCE_ENV" ]]; then
        echo -e "  ${YELLOW}FORCE MODE: already-scraped URLs will be re-scraped${NC}"
    else
        echo -e "  ${CYAN}SKIP MODE: already-scraped URLs will be skipped (use --force to override)${NC}"
    fi

    if $DO_INSTALL; then
        ensure_setup
    else
        # Try to use an existing venv first; create one if it isn't there
        if [[ ! -d "venv" ]] || ! source venv/bin/activate 2>/dev/null; then
            print_warn "venv missing or failed to activate — switching to install mode..."
            DO_INSTALL=true
            ensure_setup
        else
            # already activated above; the next source is just a safety net
            :
        fi
        # Make absolutely sure it's active
        source venv/bin/activate
    fi

    # Make sure playwright is really importable
    if ! python -c "import playwright" 2>/dev/null; then
        print_warn "playwright module not found — installing now..."
        pip install --quiet -r requirements.txt
        python -m playwright install chromium
    fi

    # Run tracking
    local started_at
    started_at=$(date +%s)
    local failed=0
    local succeeded=0

    for site in "${SITES[@]}"; do
        if run_site "$site"; then
            succeeded=$((succeeded + 1))
        else
            failed=$((failed + 1))
            print_err "Failed to run $site"
        fi
    done

    # Elapsed time
    local elapsed=$(( $(date +%s) - started_at ))
    local mins=$(( elapsed / 60 ))
    local secs=$(( elapsed % 60 ))

    print_header "Done"
    echo -e "  Succeeded: ${GREEN}${succeeded}${NC}"
    echo -e "  Failed:    ${RED}${failed}${NC}"
    echo -e "  Time:      ${mins}m ${secs}s"
    echo ""

    show_dataset_summary

    if [[ $failed -gt 0 ]]; then
        exit 1
    fi
}

main "$@"