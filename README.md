# Nelson-Siegal-ZCYC-parameters-

Scraper utilities for CCIL's **N-S ZCYC Parameters** page:

- Source page: `https://www.ccilindia.com/n-s-zcyc-parameters`
- Requested extraction window: **2013-01-01 to 2025-12-31**
- Fields: `date`, `beta0`, `beta1`, `beta2`, `tau`

## What is included

- `scrape_ns_zcyc.py`: Python scraper that submits the portal form and parses table rows.
- `data/ns_zcyc_parameters_2013_2025.csv`: output CSV for the requested date range.

## Run

```bash
python scrape_ns_zcyc.py \
  --start 2013-01-01 \
  --end 2025-12-31 \
  --step-days 1 \
  --window-days 1 \
  --sleep 0.25 \
  --output data/ns_zcyc_parameters_2013_2025.csv
```

## Notes

- The CCIL public page is server-rendered with dynamic form action tokens (`p_auth`) and cookies; the scraper refreshes them from the landing page.
- The endpoint appears to return at most 2 rows per response, so the script is designed to iterate over the period and deduplicate by date.
- If historical rows are not publicly returned by the endpoint, the CSV may be sparse or empty for older periods.
