"""
Task 1 - Data Cleaning & Preparation

Author: BENIMANA Theophile - BenTech Rwanda

What this file does:
  1. Loads the raw Netflix file
  2. Fixes wrong values and fills missing ones
  3. Removes extra spaces and duplicates
  4. Standardizes text and dates
  5. Adds 4 new columns of my own
  6. Saves output/netflix_cleaned.csv (Tasks 3, 4 and 5 use it)

Run:  python task1_cleaning.py
"""

import pandas as pd
from common import (OUTPUT_FOLDER, CLEANED_FILE, banner, say,
                    save_insights, find_raw_file)

insights = []

banner("TASK 1: Cleaning the data")

# ---------------------------------------------------------------------------
# Step 1: import the data
# ---------------------------------------------------------------------------
raw = pd.read_csv(find_raw_file())
df = raw.copy()   # we clean the copy and keep "raw" for the before/after numbers

missing_before = int(raw.isna().sum().sum())
missing_key_before = int(raw[["director", "country", "rating", "duration"]].isna().sum().sum())

# ---------------------------------------------------------------------------
# Step 2: fix wrong values and fill missing ones
# ---------------------------------------------------------------------------
# A few rows have the duration inside the rating column (example: "74 min")
wrong = df["rating"].astype(str).str.contains("min", na=False)
df.loc[wrong, "duration"] = df.loc[wrong, "rating"]
df.loc[wrong, "rating"] = None

df["director"] = df["director"].fillna("Unknown")
df["country"] = df["country"].fillna("Unknown")
df["rating"] = df["rating"].fillna("Not Rated")

# ---------------------------------------------------------------------------
# Step 3: remove extra spaces and duplicates
# ---------------------------------------------------------------------------
for col in df.columns:
    if df[col].dtype == "object" or str(df[col].dtype) == "str":
        df[col] = df[col].astype("string").str.strip()

rows_before = len(df)
df = df.drop_duplicates()
df = df.drop_duplicates(subset="show_id")
df = df.drop_duplicates(subset=["title", "type", "release_year"])
duplicates_removed = rows_before - len(df)

# ---------------------------------------------------------------------------
# Step 4: standardize the values
# ---------------------------------------------------------------------------
df["type"] = df["type"].str.title().replace({"Tv Show": "TV Show", "Movies": "Movie"})

df["rating"] = df["rating"].str.upper().replace({
    "NR": "Not Rated", "UR": "Not Rated",
    "NOT RATED": "Not Rated", "UNRATED": "Not Rated",
})

# My own column 1: who is this title made for?
audience_groups = {
    "G": "Kids", "TV-Y": "Kids", "TV-Y7": "Kids", "TV-Y7-FV": "Kids", "TV-G": "Kids",
    "PG": "Parental Guidance", "TV-PG": "Parental Guidance",
    "PG-13": "Teens", "TV-14": "Teens",
    "R": "Adults", "TV-MA": "Adults", "NC-17": "Adults",
}
df["audience"] = df["rating"].map(audience_groups).fillna("Not Rated")

# Remove extra commas: "France, " becomes "France"
for col in ["country", "listed_in"]:
    df[col] = df[col].apply(
        lambda text: ", ".join([p.strip() for p in str(text).split(",") if p.strip()])
    )
df["country"] = df["country"].replace({"": "Unknown"})

# My own column 2: the first country listed is the main one
df["main_country"] = df["country"].str.split(",").str[0].str.strip()

# Dates (older pandas versions do not know format="mixed", so we have a backup)
try:
    df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce", format="mixed")
except (TypeError, ValueError):
    df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
df["year_added"] = df["date_added"].dt.year
df["release_year"] = pd.to_numeric(df["release_year"], errors="coerce")

# My own column 3: years between release and arrival on Netflix
df["years_to_netflix"] = df["year_added"] - df["release_year"]

# My own column 4: duration as a number ("90 min" -> 90, "2 Seasons" -> 2)
df["duration_number"] = pd.to_numeric(df["duration"].str.extract(r"(\d+)")[0])

# ---------------------------------------------------------------------------
# Step 5: save the cleaned file
# ---------------------------------------------------------------------------
df.to_csv(CLEANED_FILE, index=False)
missing_after = int(df[["director", "country", "rating", "duration"]].isna().sum().sum())

say(insights, f"The raw file had {len(raw):,} rows and {missing_before:,} empty cells.")
say(insights, f"I removed {duplicates_removed} duplicate rows, so {len(df):,} unique titles remain.")
say(insights, f"Empty cells in director, country, rating and duration: "
              f"{missing_key_before} before, {missing_after} after cleaning.")
say(insights, "I added 4 new columns: audience, main_country, years_to_netflix, duration_number.")

save_insights("task1", insights)
print(f"\nCleaned file saved: {CLEANED_FILE}")
