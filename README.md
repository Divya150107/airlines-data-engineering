# ASG Airlines — Data Engineering Pipeline

End-to-end pipeline for the ASG Airlines case study: ingest four raw sheets (`flights`,
`passengers`, `bookings`, `payments`), clean and validate each one, mask PII in the two tables
that hold it, and load the result into a MySQL data warehouse (`airlines_dw`). Full write-up —
architecture diagram, data model, assumptions, and per-table cleaning logic — is in
[`documentation/Airlines_Project_Documentation.docx`](documentation/Airlines_Project_Documentation.docx).

**Note on that doc:** it was written against an earlier folder layout (per-stage notebooks named
`flights.ipynb` etc., `sql/query.sql`) rather than this repo's `src/` + single-notebook shape.
The substance — findings, fixes, decisions, numbers — is unchanged and accurate; only the
file/script names it references are from that earlier layout, not this one.

## Setup

```bash
pip install -r requirements.txt
```

## Structure

```
airlines-data-engineering/
├── notebooks/airlines_pipeline.ipynb   <- run this; the pipeline orchestrator
├── src/                                <- importable modules, called by the notebook
├── data/{raw,cleaned}/
├── logs/pipeline.log                   <- created on run; see "Error handling & logging" below
├── sql/airlines_analysis.sql           <- KPI queries against airlines_dw
├── powerbi/                            <- dashboard (.pbix) + screenshots/
├── documentation/
├── requirements.txt
└── README.md
```

## Running it

Open and run `notebooks/airlines_pipeline.ipynb` top to bottom (Jupyter's default working
directory is the notebook's own folder, which is what the relative paths inside it assume).

It calls straight into `src/`, in this order:

| Module | Function | What it does |
|---|---|---|
| `ingestion.py` | `load_all()` | Loads all 4 raw sheets. `passengers` read with `dtype={"aadhaar_id": str}` — pandas would otherwise infer that all-digit column as `int64` and silently drop leading zeros. |
| `ingestion.py` | `profile(df, key_col)` | Ingestion-time data quality check: null counts, duplicate-key count. |
| `flights_cleaning.py` | `clean_flights(df)` | Drops 15 exact-duplicate rows; imputes 69 missing airlines from the `flight_id` prefix; detects (and deliberately does not silently alter) the `6F250` `flight_id` collision — two genuinely different flights share that ID, resolved later at the SQL layer with a surrogate key, not here; corrects `SJ192`'s overnight/day-off timestamp fault, verified by cross-checking against the sheet's own `duration` column (mismatches drop from 1 to 0 after the fix). |
| `passengers_cleaning.py` | `clean_passengers(df)` | Dedupes 39 same-identity rows (kept first — these are the same person recorded inconsistently across source systems, not different people); fills missing `last_name`; cross-validates age against date of birth; validates email/phone/Aadhaar/ID formats. |
| `bookings_cleaning.py` | `clean_bookings(df)` | Format-validates all ID columns; leaves `status` nulls (45) and literal `'INVALID'` values (30) unresolved on purpose — no reliable signal for the correct default. |
| `payments_cleaning.py` | `clean_payments(df)` | Coerces `amount` to numeric, catching both nulls and literal `'INVALID'` strings (78 total) in one pass; flags invalid amounts via `(amount <= 0) | amount.isna()` — `NaN <= 0` alone is `False` in pandas and would silently miss every null row. |
| `pii_masking.py` | `mask_passengers(df)`, `mask_bookings(df)` | Masking technique chosen per column by actual re-identification risk: `first_name` kept (weak identifier alone), `last_name` reduced to an initial (the full name together is what's identifying), `email`/`phone`/`aadhaar_id`/`passport_number` partially masked, `emergency_contact_name` fully redacted (no analytical value at all). |

The notebook itself is the orchestrator — it's the only place file I/O and the MySQL load happen,
so the `src/` functions stay pure (DataFrame in, DataFrame out) and are actually importable/
testable on their own. Its last cell loads `payments` into MySQL via `mysql.connector`
(credentials from `~/.my.cnf`, never hardcoded) and correctly inserts `NULL` for the 78 invalid-
amount rows rather than `0`.

**Not scripted**: the `passengers`/`bookings` MySQL reload from the masked files was done
interactively in MySQL Workbench (staging table + `LOAD DATA LOCAL INFILE` + `UPDATE ... JOIN`) —
there's no saved script for that specific step, and the notebook says so rather than implying
it's automated.

## Error handling & logging

Lives entirely in the notebook (the orchestrator) and `ingestion.py` — deliberately not inside
`src/*_cleaning.py`, which stay untouched ports of the original scripts. Each stage (ingestion,
each `clean_x()` call, masking, the MySQL load) is wrapped in `try/except` that logs a clear
success/failure message to both the console and `logs/pipeline.log`; the MySQL load additionally
rolls back on failure and guarantees the connection/cursor close via `finally`. `ingestion.py`
raises a specific `FileNotFoundError` naming the expected path if the raw workbook is missing,
instead of a raw pandas traceback — verified directly by temporarily removing the file and
confirming the clear error, then restoring it and re-confirming a clean run.

## Verified state

Re-running the notebook from a clean slate (outputs cleared, `data/cleaned/` emptied) reproduces
exactly: `flights` 1020→1005, `passengers`/`bookings`/`payments` 1000 rows each, 0 invalid
Aadhaar values, 78 invalid payment amounts, and a MySQL load reporting 1000 rows / 78 null —
matching every number already verified against the original scripts this pipeline was refactored
from.
