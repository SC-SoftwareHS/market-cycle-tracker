#!/usr/bin/env python3
"""
Market Data Updater for Market Cycle Tracker
Fetches Shiller CAPE (Cyclically Adjusted PE) data and derived metrics.

Data sources:
  - Robert Shiller's dataset from Yale (historical monthly CAPE since 1881)
  - multpl.com for current/recent CAPE values and other metrics

Outputs:
  - data/current_market.json    (current snapshot with derived metrics)
  - data/cape_historical.json   (monthly CAPE data from 1881 to present)
"""

import json
import re
import sys
from datetime import datetime, date
from pathlib import Path

import requests
from bs4 import BeautifulSoup
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}


def scrape_number(url):
    """Scrape a numeric value from a multpl.com page."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        el = soup.select_one("#current")
        if el:
            text = el.get_text(strip=True)
            if ":" in text:
                after_colon = text.split(":")[1]
                match = re.search(r'[\d,]+\.?\d*', after_colon)
                if match:
                    return float(match.group().replace(",", ""))
            match = re.search(r'\d+\.\d+', text)
            if match:
                return float(match.group().replace(",", ""))
    except Exception as e:
        print(f"Warning: Could not scrape {url}: {e}")
    return None


def scrape_table_values(url, limit=60):
    """Scrape monthly values from a multpl.com table page."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.select_one("table#datatable")
        if not table:
            return []
        rows = table.select("tr")[1:limit + 1]
        results = []
        for row in rows:
            cells = row.select("td")
            if len(cells) >= 2:
                date_text = cells[0].get_text(strip=True)
                val_text = cells[1].get_text(strip=True).replace(",", "").replace("%", "")
                try:
                    val = float(val_text)
                    results.append({"date_text": date_text, "value": val})
                except ValueError:
                    continue
        return results
    except Exception as e:
        print(f"Warning: Could not scrape table {url}: {e}")
        return []


def fetch_shiller_excel():
    """
    Download Shiller's historical dataset and extract CAPE data.
    Returns list of dicts: [{date, cape, price, rate, fwd10yr}, ...]
    """
    url = "http://www.econ.yale.edu/~shiller/data/ie_data.xls"
    print("Downloading Shiller dataset from Yale...")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"Error downloading Shiller data: {e}")
        return None

    tmp_path = DATA_DIR / "ie_data.xls"
    tmp_path.write_bytes(resp.content)

    try:
        df = pd.read_excel(str(tmp_path), sheet_name="Data", header=None)
    except Exception as e:
        print(f"Error reading Excel: {e}")
        return None
    finally:
        if tmp_path.exists():
            tmp_path.unlink()

    HEADER_ROW = 7
    COL_DATE = 0
    COL_PRICE = 1
    COL_RATE = 6
    COL_CAPE = 12
    COL_FWD_10YR = 19

    records = []
    for i in range(HEADER_ROW + 1, len(df)):
        date_val = df.iloc[i, COL_DATE]
        if pd.isna(date_val):
            continue
        try:
            date_float = float(date_val)
        except (ValueError, TypeError):
            continue
        if date_float < 1871 or date_float > 2030:
            continue

        year = int(date_float)
        month_frac = date_float - year
        month = max(1, min(12, round(month_frac * 12) + 1))

        cape = None
        cape_raw = df.iloc[i, COL_CAPE] if len(df.columns) > COL_CAPE else None
        if pd.notna(cape_raw):
            try:
                cape = round(float(cape_raw), 2)
                if cape <= 0 or cape > 200:
                    cape = None
            except (ValueError, TypeError):
                pass

        price = None
        price_raw = df.iloc[i, COL_PRICE]
        if pd.notna(price_raw):
            try:
                price = round(float(price_raw), 2)
            except (ValueError, TypeError):
                pass

        rate = None
        rate_raw = df.iloc[i, COL_RATE] if len(df.columns) > COL_RATE else None
        if pd.notna(rate_raw):
            try:
                rate = round(float(rate_raw), 2)
            except (ValueError, TypeError):
                pass

        fwd10yr = None
        if len(df.columns) > COL_FWD_10YR:
            fwd_raw = df.iloc[i, COL_FWD_10YR]
            if pd.notna(fwd_raw):
                try:
                    fwd10yr = round(float(fwd_raw) * 100, 2)
                except (ValueError, TypeError):
                    pass

        if cape is not None:
            records.append({
                "date": f"{year}-{month:02d}",
                "cape": cape,
                "price": price,
                "rate": rate,
                "fwd10yr": fwd10yr,
            })

    print(f"Parsed {len(records)} monthly CAPE records from Shiller dataset")
    return records


def fill_recent_cape(historical, multpl_values):
    """Append recent monthly CAPE values from multpl.com newer than Shiller data."""
    if not historical or not multpl_values:
        return

    last_date = historical[-1]["date"]
    last_year = int(last_date[:4])
    last_month = int(last_date[5:7])

    month_names = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }

    added = 0
    for entry in multpl_values:
        date_text = entry["date_text"].lower()
        cape_val = entry["value"]
        parts = date_text.replace(",", "").split()
        if len(parts) >= 3:
            month_str = parts[0][:3]
            month_num = month_names.get(month_str)
            try:
                year_num = int(parts[-1])
            except ValueError:
                continue
            if month_num and year_num:
                if year_num > last_year or (year_num == last_year and month_num > last_month):
                    date_str = f"{year_num}-{month_num:02d}"
                    if not any(r["date"] == date_str for r in historical):
                        historical.append({
                            "date": date_str,
                            "cape": round(cape_val, 2),
                            "price": None,
                            "rate": None,
                            "fwd10yr": None,
                        })
                        added += 1

    if added > 0:
        historical.sort(key=lambda r: r["date"])
        print(f"Added {added} recent months from multpl.com")


def compute_derived(cape, treasury_yield):
    """Compute derived metrics from current CAPE and Treasury yield."""
    implied_return = round(-0.327 * cape + 15.42, 2)
    earnings_yield = round((1 / cape) * 100, 2)

    inflation_estimate = 2.5
    real_treasury = treasury_yield - inflation_estimate if treasury_yield else None
    excess_cape_yield = round(earnings_yield - real_treasury, 2) if real_treasury is not None else None

    table = [
        (0, 12, "Screaming Buy", 90, "15%+"),
        (12, 16, "Very Attractive", 80, "12%"),
        (16, 20, "Attractive", 70, "10%"),
        (20, 25, "Fair Value", 60, "8%"),
        (25, 30, "Expensive", 45, "6%"),
        (30, 35, "Very Expensive", 35, "4%"),
        (35, 999, "Bubble Territory", 25, "2%"),
    ]

    condition = "Unknown"
    equity_alloc = 60
    expected_label = "N/A"
    for lo, hi, label, alloc, ret in table:
        if lo <= cape < hi:
            condition = label
            equity_alloc = alloc
            expected_label = ret
            break

    return {
        "impliedReturn": implied_return,
        "earningsYield": earnings_yield,
        "excessCapeYield": excess_cape_yield,
        "condition": condition,
        "equityAllocation": equity_alloc,
        "expectedReturnLabel": expected_label,
    }


def compute_percentile(cape, records):
    """Percentile rank vs all historical CAPE readings."""
    all_capes = [r["cape"] for r in records]
    if not all_capes:
        return None
    below = sum(1 for c in all_capes if c < cape)
    return round((below / len(all_capes)) * 100, 1)


def build_context(cape, percentile, records):
    """Generate contextual narrative sentence."""
    all_capes = [r["cape"] for r in records]
    mean_cape = round(sum(all_capes) / len(all_capes), 1)
    max_rec = max(records, key=lambda r: r["cape"])

    s = (
        f"At the current CAPE of {cape}, the market is more expensive than "
        f"{percentile}% of all historical readings since 1881. "
        f"The long-run average is {mean_cape}. "
    )
    if cape > 35:
        s += f"The all-time high was {max_rec['cape']} in {max_rec['date']}, during the dot-com bubble."
    elif cape > 25:
        s += "Historically, returns from this valuation level have been below average."
    return s


def find_similar_periods(cape, records):
    """Find past periods with similar CAPE and known forward returns."""
    margin = 3.0
    similar = []
    for r in records:
        if r["fwd10yr"] is not None and abs(r["cape"] - cape) <= margin:
            similar.append({"date": r["date"], "cape": r["cape"], "fwd10yr": r["fwd10yr"]})

    seen = set()
    deduped = []
    for s in similar:
        y = s["date"][:4]
        if y not in seen:
            seen.add(y)
            deduped.append(s)
    return deduped[:10]


def determine_status(cape):
    """Determine market status classification based on CAPE."""
    if cape < 12:
        return "screaming-buy", "SCREAMING BUY"
    elif cape < 16:
        return "very-attractive", "VERY ATTRACTIVE"
    elif cape < 20:
        return "attractive", "ATTRACTIVE"
    elif cape < 25:
        return "fair", "FAIR VALUE"
    elif cape < 30:
        return "expensive", "EXPENSIVE"
    elif cape < 35:
        return "very-expensive", "VERY EXPENSIVE"
    else:
        return "bubble", "BUBBLE TERRITORY"


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Historical Shiller data
    historical = fetch_shiller_excel()
    if not historical:
        hist_path = DATA_DIR / "cape_historical.json"
        if hist_path.exists():
            print("Falling back to existing historical data")
            with open(hist_path) as f:
                historical = json.load(f)
        else:
            print("ERROR: No historical data available")
            sys.exit(1)

    # 2. Scrape recent monthly CAPE from multpl.com to fill gap
    multpl_monthly = scrape_table_values(
        "https://www.multpl.com/shiller-pe/table/by-month", limit=60
    )
    fill_recent_cape(historical, multpl_monthly)

    # 3. Current values
    current_cape = scrape_number("https://www.multpl.com/shiller-pe")
    treasury_yield = scrape_number("https://www.multpl.com/10-year-treasury-rate")
    sp500 = scrape_number("https://www.multpl.com/s-p-500-historical-prices")

    if current_cape is None and multpl_monthly:
        current_cape = multpl_monthly[0]["value"]
    if current_cape is None:
        current_cape = historical[-1]["cape"]
        print(f"Using last historical CAPE: {current_cape}")

    print(f"Current CAPE: {current_cape}")
    print(f"10Y Treasury: {treasury_yield}")
    print(f"S&P 500: {sp500}")

    # 4. Compute derived metrics
    derived = compute_derived(current_cape, treasury_yield or 4.0)
    percentile = compute_percentile(current_cape, historical)
    context = build_context(current_cape, percentile, historical)
    similar = find_similar_periods(current_cape, historical)
    status, status_text = determine_status(current_cape)

    all_capes = [r["cape"] for r in historical]
    sorted_capes = sorted(all_capes)
    mean_cape = round(sum(all_capes) / len(all_capes), 1)
    median_cape = round(sorted_capes[len(sorted_capes) // 2], 1)

    # 5. Write historical JSON
    hist_path = DATA_DIR / "cape_historical.json"
    with open(hist_path, "w") as f:
        json.dump(historical, f, separators=(",", ":"))
    print(f"Wrote {len(historical)} records to {hist_path}")

    # 6. Write current snapshot
    current = {
        "date": datetime.now().isoformat(),
        "updatedDate": date.today().isoformat(),
        "cape": current_cape,
        "pe_ratio": current_cape,
        "sp500_price": sp500,
        "treasuryYield": treasury_yield,
        "percentile": percentile,
        "status": status,
        "status_text": status_text,
        "expected_10yr_return": derived["expectedReturnLabel"],
        "description": context,
        "historical_average": mean_cape,
        "context": context,
        "similarPeriods": similar,
        "stats": {
            "mean": mean_cape,
            "median": median_cape,
            "min": min(all_capes),
            "max": max(all_capes),
            "count": len(all_capes),
        },
        "impliedReturn": derived["impliedReturn"],
        "earningsYield": derived["earningsYield"],
        "excessCapeYield": derived["excessCapeYield"],
        "condition": derived["condition"],
        "equityAllocation": derived["equityAllocation"],
        "expectedReturnLabel": derived["expectedReturnLabel"],
    }

    curr_path = DATA_DIR / "current_market.json"
    with open(curr_path, "w") as f:
        json.dump(current, f, indent=2)
    print(f"Wrote current snapshot to {curr_path}")

    # 7. Generate visualizations
    try:
        from generate_visualization import MarketVisualizationGenerator
        viz_gen = MarketVisualizationGenerator()
        viz_gen.generate_all_visualizations()
        print("Visualizations updated")
    except Exception as e:
        print(f"Warning: Could not update visualizations: {e}")

    print(f"\nSummary:")
    print(f"  CAPE Ratio: {current_cape}")
    print(f"  Status: {status_text}")
    print(f"  Percentile: {percentile}th")
    print(f"  Implied 10yr Return: {derived['impliedReturn']}%")
    print(f"  Condition: {derived['condition']}")
    print(f"  Historical records: {len(historical)}")
    print("Done!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
