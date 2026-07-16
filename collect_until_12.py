from pathlib import Path
from datetime import datetime
import subprocess
import sys
import time

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent

NOTEBOOK_01 = PROJECT_ROOT / "notebooks" / "01_live_aqi_data_fetching.ipynb"
HISTORY_PATH = PROJECT_ROOT / "data" / "processed" / "station_aqi_history.csv"

TARGET_UNIQUE_TIMESTAMPS = 12
WAIT_SECONDS = 15 * 60   # 15 minutes


def check_history():
    if not HISTORY_PATH.exists():
        print("History file not found yet.")
        return 0, 0

    df = pd.read_csv(HISTORY_PATH)

    if "timestamp" not in df.columns:
        print("timestamp column not found in history file.")
        return len(df), 0

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    rows = len(df)
    unique_timestamps = df["timestamp"].nunique()

    print("\nCurrent AQI history status:")
    print("Rows:", rows)
    print("Unique timestamps:", unique_timestamps)

    if unique_timestamps > 0:
        print("Date range:", df["timestamp"].min(), "to", df["timestamp"].max())
        print("\nTimestamp counts:")
        print(df["timestamp"].value_counts().sort_index())

    return rows, unique_timestamps


def run_notebook_01():
    print("\nRunning Notebook 01...")
    print("Time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    command = [
        sys.executable,
        "-m",
        "jupyter",
        "nbconvert",
        "--to",
        "notebook",
        "--execute",
        str(NOTEBOOK_01),
        "--inplace",
        "--ExecutePreprocessor.timeout=900"
    ]

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True
    )

    if result.returncode == 0:
        print("Notebook 01 executed successfully.")
    else:
        print("Notebook 01 failed or API was unavailable.")
        print("The script will wait and try again.")


def main():
    print("CleanAir AI automatic AQI collector started.")
    print("Target unique timestamps:", TARGET_UNIQUE_TIMESTAMPS)
    print("Checking every", WAIT_SECONDS // 60, "minutes.")
    print("Press Ctrl + C anytime to stop manually.")

    while True:
        run_notebook_01()

        rows, unique_timestamps = check_history()

        if unique_timestamps >= TARGET_UNIQUE_TIMESTAMPS:
            print("\nTarget reached.")
            print("You now have enough timestamps for Notebook 04 forecasting.")
            print("Final rows:", rows)
            print("Final unique timestamps:", unique_timestamps)
            break

        remaining = TARGET_UNIQUE_TIMESTAMPS - unique_timestamps

        print("\nStill need", remaining, "more unique timestamps.")
        print("Waiting 15 minutes before next check...")
        print("-" * 60)

        time.sleep(WAIT_SECONDS)


if __name__ == "__main__":
    main()