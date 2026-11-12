"""
Task 3 - Country-Wise Content Analysis

Author: BENIMANA Theophile - BenTech Rwanda

Question: which countries make the content on Netflix?
Needs the cleaned file from Task 1.

Run:  python task3_country_analysis.py
"""

import matplotlib.pyplot as plt
from common import (RED, DARK_RED, WHITE, OUTPUT_FOLDER, banner, say, save_chart,
                    save_insights, load_cleaned, split_values)

insights = []
df = load_cleaned()

banner("TASK 3: Which countries make Netflix content?")

# A title can have many countries, so we split them and count each one
countries = split_values(df["country"])
countries = countries[countries != "Unknown"]

country_count = countries.value_counts()
top10 = country_count.head(10)

# ---------------------------------------------------------------------------
# Chart 1: top 10 countries (leader in red, others in dark red)
# ---------------------------------------------------------------------------
plt.figure(figsize=(9, 5.5))
values = top10.sort_values()
colors = [DARK_RED] * len(values)
colors[-1] = RED
plt.barh(values.index, values.values, color=colors)
for i, v in enumerate(values.values):
    plt.text(v, i, f"  {v}", va="center", color=WHITE)
plt.title("Top 10 Countries Behind Netflix Titles")
plt.xlabel("Number of titles")
save_chart("task3_top10_countries.png")

# ---------------------------------------------------------------------------
# Chart 2 (my own idea): how international is Netflix becoming?
# ---------------------------------------------------------------------------
known = df[(df["main_country"] != "Unknown") & (df["year_added"] >= 2015)]
share = known.groupby("year_added")["main_country"].apply(
    lambda c: (c != "United States").mean() * 100
)

plt.figure(figsize=(9, 5.5))
plt.plot(share.index, share.values, marker="o", color=RED, linewidth=3)
plt.fill_between(share.index, share.values, color=RED, alpha=0.15)
for x, y in zip(share.index, share.values):
    plt.text(x, y + 1.5, f"{y:.0f}%", ha="center", fontsize=9)
plt.title("How International Is Netflix? (titles NOT led by the USA)")
plt.xlabel("Year added to Netflix")
plt.ylabel("Percent of titles")
plt.grid(alpha=0.4)
save_chart("task3_international_share.png")

# ---------------------------------------------------------------------------
# Insights
# ---------------------------------------------------------------------------
say(insights, f"{top10.index[0]} appears in {top10.iloc[0] / len(df) * 100:.1f}% "
              f"of all titles - the number 1 country.")
say(insights, f"The top 3 countries are {top10.index[0]}, {top10.index[1]} and {top10.index[2]}.")
say(insights, f"Netflix has titles from {countries.nunique()} different countries.")
if len(share) > 1:
    say(insights, f"Titles not led by the USA went from {share.iloc[0]:.0f}% in {int(share.index[0])} "
                  f"to {share.iloc[-1]:.0f}% in {int(share.index[-1])}.")

country_count.head(20).to_csv(OUTPUT_FOLDER / "task3_country_ranking.csv", header=["titles"])
save_insights("task3", insights)
