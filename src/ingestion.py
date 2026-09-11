import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

# resolved relative to this file, not the caller's working directory -- so it
# works the same whether this is run from the repo root or from a notebook in
# notebooks/ (Jupyter's default cwd is the notebook's own folder)
RAW_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "UseCase - Airlines.xlsx"


def load_sheet(sheet_name, **read_kwargs):
    """Load one sheet from the raw ASG Airlines workbook."""
    if not RAW_PATH.exists():
        raise FileNotFoundError(
            f"Raw workbook not found at {RAW_PATH}. "
            f"Expected 'UseCase - Airlines.xlsx' under data/raw/ relative to the repo root."
        )
    try:
        df = pd.read_excel(RAW_PATH, sheet_name=sheet_name, **read_kwargs)
    except ValueError as e:
        # pandas raises ValueError for a sheet name that doesn't exist in the workbook
        raise ValueError(
            f"Could not read sheet '{sheet_name}' from {RAW_PATH.name}: {e}"
        ) from e
    logger.info("Loaded sheet '%s': %d rows, %d columns", sheet_name, *df.shape)
    return df


def load_all():
    """Load all four raw sheets as a dict of DataFrames.

    aadhaar_id is read as string -- pandas would otherwise infer the
    all-digit column as int64 and silently drop leading zeros (e.g.
    '056413953767' -> 56413953767, 11 digits). The source .xlsx cells are
    already text with the leading zero intact.
    """
    return {
        "flights": load_sheet("flights"),
        "passengers": load_sheet("passengers", dtype={"aadhaar_id": str}),
        "bookings": load_sheet("bookings"),
        "payments": load_sheet("payments"),
    }


def profile(df, key_col=None):
    """Data-quality check run during ingestion: null counts, exact-duplicate
    row count, and duplicate-key count (if a key column is given)."""
    print(df.isna().sum())
    print("exact duplicate rows:", df.duplicated().sum())
    if key_col:
        print(f"duplicate {key_col}:", df[key_col].duplicated(keep=False).sum())
