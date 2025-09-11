import pytest
import pandas as pd
from datetime import datetime, date
from src.celan_and_validate.clean_and_validate import (
    clean_and_validate_hours,
    clean_and_validate_days,
    is_valid_wmo
)

# ---------------- clean_and_validate_hours ----------------
def test_clean_and_validate_hours_basic():
    df = pd.DataFrame({
        "temp": [20, -70, 100, None, 0],
        "humidity": [50, 30, None, 0, 0]
    }, index=["2025-01-01 00:00", "2025-01-01 01:00", "2025-01-01 02:00", "2025-01-01 03:00", "2025-01-01 04:00"])
    
    result = clean_and_validate_hours(df)

    # Only rows with temp within MIN_TEMP and MAX_TEMP, not all zeros or None
    assert all(result["temp"].between(-60, 90))
    # Check 'time' column exists
    assert "time" in result.columns
    # No rows where all non-time columns are 0/None
    assert not ((result.drop(columns=["time"]) == 0) | (result.drop(columns=["time"]).isna())).all(axis=1).any()

def test_clean_and_validate_hours_coco_column():
    df = pd.DataFrame({
        "temp": [25],
        "coco": ["1", "2", None, "a", "3.0"][:1]
    }, index=[0])
    result = clean_and_validate_hours(df)
    # Check coco converted to Int64 type if exists
    assert "coco" not in result.columns or result["coco"].dtype.name == "Int64"

# ---------------- clean_and_validate_days ----------------
def test_clean_and_validate_days_basic():
    df = pd.DataFrame({
        "tavg": [20, -70, 100, None, 0],
        "precip": [0, 1, None, 0, 0]
    }, index=["2025-01-01","2025-01-02","2025-01-03","2025-01-04","2025-01-05"])
    
    result = clean_and_validate_days(df)
    # Only rows with tavg in bounds
    assert all((result["tavg"] >= -60) & (result["tavg"] <= 90))
    # 'time' column exists
    assert "time" in result.columns
    # 'time' column is date
    assert isinstance(result["time"].iloc[0], date)

# ---------------- is_valid_wmo ----------------
@pytest.mark.parametrize("input_val,expected", [
    (123, True),
    ("123", True),
    ("123.0", True),
    ("123.4", False),
    (None, False),
    (pd.NA, False),
    (float("nan"), False),
    ("", False),
    ("<NA>", False),
    ("NA", False),
    ("n/a", False),
    ("abc", False),
])
def test_is_valid_wmo(input_val, expected):
    assert is_valid_wmo(input_val) == expected
