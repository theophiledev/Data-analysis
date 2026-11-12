"""
Task 4 - Trend Analysis by Release Year

Author: BENIMANA Theophile - BenTech Rwanda

Question: how did Netflix content change over the years?
Needs the cleaned file from Task 1.

Run:  python task4_trend_analysis.py
"""

import matplotlib.pyplot as plt
from common import (RED, WHITE, GREY, OUTPUT_FOLDER, banner, say, save_chart,
                    save_insights, load_cleaned)

insights = []
df = load_cleaned()

banner("TASK 4: How did content change over the years?")

# We look at titles released from the year 2000
recent = df[df["release_year"] >= 2000]
per_year = recent.groupby(["release_year", "type"]).size().unstack(fill_value=0)
total_per_year = recent.groupby("release_year").size()
peak_year = int(total_per_year.idxmax())

# ---------------------------------------------------------------------------
# Chart 3: movies vs TV shows by release year
# ---------------------------------------------------------------------------
plt.figure(figsize=(10, 5.5))
line_colors = {"Movie": RED, "TV Show": WHITE}
for kind in per_year.columns:
    plt.plot(per_year.index, per_year[kind], marker="o", linewidth=2.5,
             color=line_colors.get(kind, GREY), label=kind)
plt.axvline(peak_year, color=GREY, linestyle="--")
plt.text(peak_year, plt.ylim()[1] * 0.95, f" Peak: {peak_year}", color=WHITE)
plt.title("Netflix Titles by Release Year")
plt.xlabel("Release year")
plt.ylabel("Number of titles")
plt.legend()
plt.grid(alpha=0.4)
save_chart("task4_titles_by_release_year.png")

# ---------------------------------------------------------------------------
# Growth and decline compared with the year before
# ---------------------------------------------------------------------------
growth = total_per_year.pct_change() * 100
say(insights, f"Peak year: {peak_year} with {total_per_year.max()} titles released.")
say(insights, f"Biggest growth: {int(growth.idxmax())} ({growth.max():.0f}% more than the year before).")
say(insights, f"Biggest decline: {int(growth.idxmin())} ({growth.min():.0f}% compared with the year before).")

# ---------------------------------------------------------------------------
# Chart 4 (my own idea): how old is a title when it arrives on Netflix?
# ---------------------------------------------------------------------------
lag = df[df["years_to_netflix"] >= 0].groupby("year_added")["years_to_netflix"].mean()
lag = lag[lag.index >= 2015]

plt.figure(figsize=(9, 5.5))
plt.bar(lag.index.astype(int), lag.values, color=RED)
for x, y in zip(lag.index.astype(int), lag.values):
    plt.text(x, y + 0.1, f"{y:.1f}", ha="center", fontsize=10)
plt.title("Average Age of a Title When Netflix Adds It")
plt.xlabel("Year added to Netflix")
plt.ylabel("Years since release")
save_chart("task4_content_age.png")

if len(lag) > 1:
    say(insights, f"Average content age moved from {lag.iloc[0]:.1f} years ({int(lag.index[0])}) "
                  f"to {lag.iloc[-1]:.1f} years ({int(lag.index[-1])}).")

total_per_year.to_csv(OUTPUT_FOLDER / "task4_titles_per_year.csv", header=["titles"])
save_insights("task4", insights)
