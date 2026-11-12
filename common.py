"""
common.py - settings and small helper functions used by every task.

Project : Netflix Content Analysis (Data Analysis Using Python Internship)
Company : Auspify Technologies
Author  : BENIMANA Theophile - BenTech Rwanda

You do not run this file directly. The task files import it.
"""

import json
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Netflix colours
# ---------------------------------------------------------------------------
RED = "#E50914"
DARK_RED = "#8C0A10"
WHITE = "#F5F5F1"
GREY = "#6B6B6B"
BLACK = "#141414"

# ---------------------------------------------------------------------------
# Folders and files
# ---------------------------------------------------------------------------
BASE_FOLDER = Path(__file__).parent
OUTPUT_FOLDER = BASE_FOLDER / "output"
OUTPUT_FOLDER.mkdir(exist_ok=True)

RAW_FILE_NAME = "netflix_titles.csv"                 # put the dataset next to the code
CLEANED_FILE = OUTPUT_FOLDER / "netflix_cleaned.csv"  # created by task1_cleaning.py

# ---------------------------------------------------------------------------
# One dark style for all charts
# ---------------------------------------------------------------------------
plt.rcParams.update({
    "figure.facecolor": BLACK, "axes.facecolor": BLACK, "savefig.facecolor": BLACK,
    "axes.edgecolor": "#444444", "axes.labelcolor": WHITE, "text.color": WHITE,
    "xtick.color": WHITE, "ytick.color": WHITE, "grid.color": "#333333",
    "axes.titlesize": 15, "axes.titleweight": "bold", "font.size": 11,
    "axes.spines.top": False, "axes.spines.right": False,
    "legend.facecolor": BLACK, "legend.edgecolor": "#444444",
})


def banner(text):
    """Print a title line so the console output is easy to read."""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def save_chart(file_name):
    """Save the chart we just drew into the output folder."""
    plt.tight_layout()
    plt.savefig(OUTPUT_FOLDER / file_name, dpi=150)
    plt.close()


def say(insights, sentence):
    """Print one finding and also keep it, so the report page can use it."""
    print("  *", sentence)
    insights.append(sentence)


def save_insights(task_name, insights):
    """Write the findings of one task to a small JSON file."""
    path = OUTPUT_FOLDER / f"insights_{task_name}.json"
    path.write_text(json.dumps(insights, indent=2), encoding="utf-8")


def load_insights(task_name):
    """Read the findings of one task (empty list if the task was not run)."""
    path = OUTPUT_FOLDER / f"insights_{task_name}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return []


def find_raw_file():
    """Find the original Netflix csv file."""
    wanted = BASE_FOLDER / RAW_FILE_NAME
    if wanted.exists():
        return wanted

    # If the file has another name, use it when it is the only csv here
    csv_files = list(BASE_FOLDER.glob("*.csv"))
    if len(csv_files) == 1:
        return csv_files[0]

    raise SystemExit(
        f"\nI could not find the dataset.\n"
        f"Please copy the Netflix csv file into this folder:\n  {BASE_FOLDER}\n"
        f"and name it {RAW_FILE_NAME}"
    )


def load_cleaned():
    """Load the cleaned data created by Task 1."""
    if not CLEANED_FILE.exists():
        raise SystemExit("\nCleaned data not found. Please run task1_cleaning.py first.")
    return pd.read_csv(CLEANED_FILE, parse_dates=["date_added"])


def split_values(series):
    """Turn 'India, France' style cells into one value per row."""
    return series.str.split(",").explode().str.strip()
