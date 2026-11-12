"""
Task 5 - Content Rating & Genre Analysis

Author: BENIMANA Theophile - BenTech Rwanda

Question: who is Netflix content made for, and which genres are most common?
Needs the cleaned file from Task 1.

Run:  python task5_rating_genre.py
"""

import pandas as pd
import matplotlib.pyplot as plt
from common import (RED, DARK_RED, WHITE, GREY, BLACK, OUTPUT_FOLDER, banner, say,
                    save_chart, save_insights, load_cleaned)

insights = []
df = load_cleaned()

banner("TASK 5: Who is Netflix content made for?")

rating_count = df["rating"].value_counts()

# One row per genre (a title with 3 genres becomes 3 rows)
genres = df[["type", "audience", "listed_in"]].copy()
genres["genre"] = genres["listed_in"].str.split(",")
genres = genres.explode("genre").reset_index(drop=True)
genres["genre"] = genres["genre"].str.strip()
genre_count = genres["genre"].value_counts()
top_genres = genre_count.head(10)

# ---------------------------------------------------------------------------
# Chart 5: ratings for Movies vs TV Shows
# ---------------------------------------------------------------------------
rating_by_type = pd.crosstab(df["rating"], df["type"])
rating_by_type.plot(kind="bar", figsize=(10, 5.5),
                    color=[RED if c == "Movie" else WHITE for c in rating_by_type.columns])
plt.title("Ratings: Movies vs TV Shows")
plt.xlabel("Rating")
plt.ylabel("Number of titles")
plt.xticks(rotation=45)
save_chart("task5_rating_by_type.png")

# ---------------------------------------------------------------------------
# Chart 6 (my own idea): audience donut
# ---------------------------------------------------------------------------
audience_count = df["audience"].value_counts()
donut_colors = [RED, WHITE, GREY, DARK_RED, "#B3B3B3"][:len(audience_count)]

plt.figure(figsize=(7, 6))
plt.pie(audience_count.values, labels=audience_count.index, colors=donut_colors,
        autopct="%1.0f%%", startangle=90, pctdistance=0.8,
        wedgeprops={"width": 0.4, "edgecolor": BLACK}, textprops={"color": WHITE})
plt.title("Who Is Netflix Content Made For?")
save_chart("task5_audience_donut.png")

# ---------------------------------------------------------------------------
# Chart 7: interactive chart saved as an HTML file
# ---------------------------------------------------------------------------
genre_audience = pd.crosstab(genres["genre"], genres["audience"]).loc[top_genres.index]

try:
    import plotly.express as px
    table = genre_audience.reset_index().melt(id_vars="genre", var_name="audience",
                                              value_name="titles")
    fig = px.bar(table, x="genre", y="titles", color="audience", barmode="stack",
                 template="plotly_dark",
                 title="Top 10 Genres and Their Audience (click the legend to filter)",
                 color_discrete_sequence=[RED, WHITE, GREY, DARK_RED, "#B3B3B3"])
    fig.write_html(OUTPUT_FOLDER / "task5_interactive_genre_audience.html")
    print("  Interactive chart saved: task5_interactive_genre_audience.html")
except ImportError:
    print("  (Plotly is not installed. Run: pip install plotly - then run this file again)")

# ---------------------------------------------------------------------------
# Insights
# ---------------------------------------------------------------------------
adult_share = (df["audience"] == "Adults").mean() * 100

say(insights, f"The most common genre is '{top_genres.index[0]}' ({top_genres.iloc[0]} titles).")
say(insights, f"The most common rating is '{rating_count.index[0]}' ({rating_count.iloc[0]} titles).")
say(insights, f"{adult_share:.0f}% of all titles are made for adults.")

if "Adults" in genre_audience.columns:
    adult_by_genre = (genre_audience["Adults"] / genre_audience.sum(axis=1) * 100)
    adult_by_genre = adult_by_genre.sort_values(ascending=False)
    say(insights, f"Among the top genres, '{adult_by_genre.index[0]}' has the highest "
                  f"adult share ({adult_by_genre.iloc[0]:.0f}%).")

genre_audience.to_csv(OUTPUT_FOLDER / "task5_genre_by_audience.csv")
save_insights("task5", insights)
