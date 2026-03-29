#!/usr/bin/env python3
"""Scrape CCIL N-S ZCYC parameters for a date range.

The portal accepts a date range submission and (as observed publicly) returns up to
2 records in a response. This script walks the period day-by-day to build a daily
series when available.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import html
import re
import time
import urllib.parse
import urllib.request
import http.cookiejar
from pathlib import Path

BASE_URL = "https://www.ccilindia.com/n-s-zcyc-parameters"
FORM_PATTERN = re.compile(r'form class="cust_form[^\"]*" action="([^\"]+)"')
ROW_PATTERN = re.compile(
    r"<tr>\s*"
    r"<td align=\"center\">([^<]+)</td>\s*"
    r"<td align=\"center\">([^<]+)</td>\s*"
    r"<td align=\"center\">([^<]+)</td>\s*"
    r"<td align=\"center\">([^<]+)</td>\s*"
    r"<td align=\"center\">([^<]+)</td>\s*"
    r"</tr>",
    re.S,
)

FROM_KEY = "_CcilNsZcycParamWeb_CcilNsZcycParamWebPortlet_INSTANCE_ykcb_fromDate"
TO_KEY = "_CcilNsZcycParamWeb_CcilNsZcycParamWebPortlet_INSTANCE_ykcb_toDate"


def date_range(start: dt.date, end: dt.date):
    current = start
    while current <= end:
        yield current
        current += dt.timedelta(days=1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default="2013-01-01", help="Start date YYYY-MM-DD")
    parser.add_argument("--end", default="2025-12-31", help="End date YYYY-MM-DD")
    parser.add_argument("--sleep", type=float, default=0.25, help="Delay between requests (seconds)")
    parser.add_argument("--step-days", type=int, default=1, help="Increment between successive queries")
    parser.add_argument("--window-days", type=int, default=1, help="Query window size (to = from + window-days)")
    parser.add_argument("--output", default="data/ns_zcyc_parameters_2013_2025.csv", help="Output CSV path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    start = dt.date.fromisoformat(args.start)
    end = dt.date.fromisoformat(args.end)
    if start > end:
        raise SystemExit("start date must be <= end date")

    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

    initial_html = opener.open(BASE_URL, timeout=60).read().decode("utf-8", errors="ignore")
    m = FORM_PATTERN.search(initial_html)
    if not m:
        raise SystemExit("Could not locate search form action on CCIL page")

    action_url = html.unescape(m.group(1))

    unique_rows: dict[str, tuple[str, str, str, str]] = {}

    step = dt.timedelta(days=max(1, args.step_days))
    window = dt.timedelta(days=max(1, args.window_days))

    day = start
    while day <= end:
        day2 = day + window
        payload = urllib.parse.urlencode({FROM_KEY: day.isoformat(), TO_KEY: day2.isoformat()}).encode("utf-8")
        req = urllib.request.Request(action_url, data=payload)
        response_html = opener.open(req, timeout=60).read().decode("utf-8", errors="ignore")

        for row in ROW_PATTERN.findall(response_html):
            date_text, beta0, beta1, beta2, tau = [cell.strip() for cell in row]
            day_only = date_text.split(" ")[0]
            if start.isoformat() <= day_only <= end.isoformat():
                unique_rows[day_only] = (beta0, beta1, beta2, tau)

        time.sleep(args.sleep)
        day += step

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "beta0", "beta1", "beta2", "tau"])
        for d in sorted(unique_rows):
            writer.writerow([d, *unique_rows[d]])

    print(f"Saved {len(unique_rows)} rows to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
