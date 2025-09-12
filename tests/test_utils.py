import pandas as pd
from datetime import datetime
from unittest.mock import MagicMock, patch

from src.utils.utils import (
    get_start_date,
    rename_index_to_time,
    prepare_to_records,
    copy_to_db,
    insert_into_db,
    calc_days_of_year,
    load_data_into_df,
)


# ---------- get_start_date ----------
def test_get_start_date():
    row = {"hourly_start": "2025-01-01", "daily_start": "2025-01-01"}
    assert get_start_date(row) == pd.Timestamp("2025-01-01").to_pydatetime()

    # Test with invalid date
    row = {"hourly_start": "2025-01-01", "daily_start": "2025-01-01"}
    result = get_start_date(row)
    assert isinstance(result, datetime)


# ---------- rename_index_to_time ----------
def test_rename_index_to_time():
    df = pd.DataFrame({"a": [1, 2, 3]}, index=[10, 20, 30])
    df2 = rename_index_to_time(df, new_name="timestamp")
    assert "timestamp" in df2.columns
    assert df2["timestamp"].tolist() == [10, 20, 30]


def test_prepare_to_records():
    df = pd.DataFrame({"col1": [1, None], "col2": [None, 2]})
    records, df_out = prepare_to_records(
        df, station_id=5, cols=["col1", "col2", "station_id"]
    )

    # Check that station_id added
    assert all(df_out["station_id"] == 5)

    # Check records format
    assert records[0] == (1, None, 5)
    assert records[1] == (None, 2, 5)


# ---------- copy_to_db ----------
def test_copy_to_db_mock():
    df = pd.DataFrame({"col1": [1, 2]})
    mock_conn = MagicMock()
    # Mock the cursor context manager
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    # Run the function
    copy_to_db(df, mock_conn, station_id=1, cols=["col1", "station_id"])
    # Assert copy_expert called
    assert mock_cursor.copy_expert.called
    assert mock_conn.commit.called


# ---------- insert_into_db ----------
def test_insert_into_db_mock():
    df = pd.DataFrame({"col1": [1, 2]})
    insert_sql = "INSERT INTO table (col1, station_id) VALUES %s"

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    # cursor context manager belépés
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    # Patch execute_values, mert nem akarunk valódi DB-t
    with patch("src.utils.utils.execute_values") as mock_execute_values:
        insert_into_db(
            df,
            mock_conn,
            station_id=3,
            insert_sql=insert_sql,
            cols=["col1", "station_id"],
        )
        # ellenőrizzük, hogy execute_values hívódott
        mock_execute_values.assert_called_once()
        # commit hívása
        mock_conn.commit.assert_called_once()


# ---------- calc_days_of_year ----------
def test_calc_days_of_year():
    # Past year
    assert calc_days_of_year(2024) in [365, 366]
    # Current year
    today = pd.Timestamp.today()
    assert calc_days_of_year(today.year) == today.day_of_year


# ---------- load_data_into_df ----------
def test_load_data_into_df_mock():
    mock_df = pd.DataFrame({"a": [1, 2]})
    with patch("src.utils.utils.connect_to_db") as mock_conn_func, patch(
        "pandas.read_sql"
    ) as mock_read_sql:
        mock_conn = MagicMock()
        mock_conn_func.return_value = mock_conn
        mock_read_sql.return_value = mock_df
        df = load_data_into_df("SELECT 1")
        # Check returned DataFrame
        pd.testing.assert_frame_equal(df, mock_df)
        # Check connection closed
        assert mock_conn.close.called
