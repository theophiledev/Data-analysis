"""
Task 6 (Advanced) - Netflix Business Insights Report

Author: BENIMANA Theophile - BenTech Rwanda

This file follows the 5 steps of the task:
  Step 1: complete exploratory data analysis (EDA)
  Step 2: find key content trends and patterns
  Step 3: build multiple visual dashboards
  Step 4: write actionable business insights
  Step 5: build the final executive report (one responsive HTML page)

Needs the cleaned file from Task 1.
Run:  python task6_business_insights.py
Then open: output/Netflix_Business_Insights_Report.html
"""

import base64
import calendar
import html

import pandas as pd
import matplotlib.pyplot as plt

from common import (RED, DARK_RED, WHITE, GREY, BLACK, OUTPUT_FOLDER, banner,
                    save_insights, load_cleaned, find_raw_file, split_values)

# Colours for the audience groups (used in several charts)
AUDIENCE_COLORS = {"Adults": RED, "Teens": WHITE, "Parental Guidance": GREY,
                   "Kids": "#B3B3B3", "Not Rated": "#444444"}

df = load_cleaned()
raw = pd.read_csv(find_raw_file())

movies = df[df["type"] == "Movie"]
shows = df[df["type"] == "TV Show"]


# ===========================================================================
# STEP 1 - EXPLORATORY DATA ANALYSIS
# ===========================================================================
banner("TASK 6 - STEP 1: Exploratory data analysis")

# 1a. Size of the data and missing values in the ORIGINAL file
column_summary = pd.DataFrame({
    "Column": raw.columns,
    "Type": [str(t) for t in raw.dtypes],
    "Missing": raw.isna().sum().values,
    "Missing %": (raw.isna().mean() * 100).round(1).values,
    "Unique values": raw.nunique().values,
})
column_summary.to_csv(OUTPUT_FOLDER / "task6_eda_column_summary.csv", index=False)

print(f"  The raw file has {len(raw):,} rows and {raw.shape[1]} columns.")
print(f"  After cleaning we have {len(df):,} unique titles.")
print("\n  Missing values in the original file:")
print(column_summary[column_summary["Missing"] > 0][["Column", "Missing", "Missing %"]]
      .to_string(index=False))

# 1b. Numbers summary (release year, duration, years until added)
numbers_summary = df[["release_year", "duration_number", "years_to_netflix"]].describe().round(1).T
numbers_summary.to_csv(OUTPUT_FOLDER / "task6_eda_numbers_summary.csv")
print("\n  Summary of the main number columns:")
print(numbers_summary.to_string())

# 1c. Basic distributions
print("\n  Type split:")
print(df["type"].value_counts().to_string())
print("\n  Audience split:")
print(df["audience"].value_counts().to_string())


# ===========================================================================
# STEP 2 - KEY CONTENT TRENDS AND PATTERNS
# ===========================================================================
banner("TASK 6 - STEP 2: Finding trends and patterns")

df["month_added"] = df["date_added"].dt.month

# Titles added each year (all years) and by type (from 2015)
added_per_year = df.groupby("year_added").size()
added_by_type = (df[df["year_added"] >= 2015]
                 .groupby(["year_added", "type"]).size().unstack(fill_value=0)
                 .reindex(columns=["Movie", "TV Show"], fill_value=0))
tv_share = added_by_type["TV Show"] / added_by_type.sum(axis=1) * 100

# Which month does Netflix add the most titles?
month_counts = df["month_added"].value_counts().reindex(range(1, 13), fill_value=0)

# Countries (a title can have many countries, so we count each one)
countries = split_values(df["country"])
countries = countries[countries != "Unknown"]
country_count = countries.value_counts()

known_country = df[df["main_country"] != "Unknown"]
non_us_overall = (known_country["main_country"] != "United States").mean() * 100
non_us_by_year = (known_country[known_country["year_added"] >= 2015]
                  .groupby("year_added")["main_country"]
                  .apply(lambda c: (c != "United States").mean() * 100))

# Genres (one row per genre)
genre_rows = df[["year_added", "type", "audience", "listed_in"]].copy()
genre_rows["genre"] = genre_rows["listed_in"].str.split(",")
genre_rows = genre_rows.explode("genre")
genre_rows["genre"] = genre_rows["genre"].str.strip()
genre_count = genre_rows["genre"].value_counts()
top5_genres = genre_count.head(5).index
genre_by_year = (genre_rows[genre_rows["genre"].isin(top5_genres) & (genre_rows["year_added"] >= 2015)]
                 .groupby(["year_added", "genre"]).size().unstack(fill_value=0))

# Audience mix by year (percent)
audience_by_year = (pd.crosstab(df[df["year_added"] >= 2015]["year_added"],
                                df[df["year_added"] >= 2015]["audience"],
                                normalize="index") * 100)

# How old is a title when it is added?
age_by_year = (df[df["years_to_netflix"] >= 0].groupby("year_added")["years_to_netflix"].mean())
age_by_year = age_by_year[age_by_year.index >= 2015]

print(f"  Years with additions: {int(added_per_year.index.min())} to {int(added_per_year.index.max())}")
print(f"  Busiest month for additions: {calendar.month_name[int(month_counts.idxmax())]}")
print(f"  Number of countries: {countries.nunique()}, number of genres: {genre_count.size}")


# ===========================================================================
# STEP 3 - VISUAL DASHBOARDS
# ===========================================================================
banner("TASK 6 - STEP 3: Building dashboards")


def save_dashboard(fig, file_name, title):
    """Add the title, fix spacing and save one dashboard picture."""
    fig.suptitle(title, fontsize=20, fontweight="bold", color=WHITE)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(OUTPUT_FOLDER / file_name, dpi=130)
    plt.close(fig)
    print("  Saved:", file_name)


def kpi_strip(ax, items):
    """Draw a row of big numbers at the top of a dashboard."""
    ax.axis("off")
    step = 1 / len(items)
    for i, (value, label) in enumerate(items):
        x = step * i + step / 2
        ax.text(x, 0.50, value, ha="center", va="bottom", fontsize=24,
                fontweight="bold", color=RED, transform=ax.transAxes)
        ax.text(x, 0.45, label, ha="center", va="top", fontsize=11,
                color=WHITE, transform=ax.transAxes)


# ---------------------------------------------------------------------------
# Dashboard 1 - Executive overview
# ---------------------------------------------------------------------------
avg_age = df[df["years_to_netflix"] >= 0]["years_to_netflix"].mean()

fig = plt.figure(figsize=(14, 9))
grid = fig.add_gridspec(3, 3, height_ratios=[0.45, 2, 2])

kpi_strip(fig.add_subplot(grid[0, :]), [
    (f"{len(df):,}", "Titles"),
    (f"{len(movies) / len(df) * 100:.0f}%", "Movies"),
    (f"{len(shows) / len(df) * 100:.0f}%", "TV Shows"),
    (f"{countries.nunique()}", "Countries"),
    (f"{genre_count.size}", "Genres"),
    (f"{non_us_overall:.0f}%", "Not led by USA"),
])

ax = fig.add_subplot(grid[1, 0])
type_count = df["type"].value_counts()
type_colors = [RED if name == "Movie" else WHITE for name in type_count.index]
_, _, percent_texts = ax.pie(type_count.values, labels=type_count.index, colors=type_colors,
                             autopct="%1.0f%%", startangle=90, pctdistance=0.78,
                             wedgeprops={"width": 0.4, "edgecolor": BLACK},
                             textprops={"color": WHITE})
for text, color in zip(percent_texts, type_colors):
    text.set_color(BLACK if color == WHITE else WHITE)   # readable on the white slice
ax.set_title("Movies vs TV Shows")

ax = fig.add_subplot(grid[1, 1:])
ax.bar(added_per_year.index.astype(int), added_per_year.values, color=RED)
ax.set_title("Titles Added to Netflix per Year")
ax.set_xlabel("Year added")
ax.set_ylabel("Titles")

ax = fig.add_subplot(grid[2, 0])
top5_countries = country_count.head(5).sort_values()
ax.barh(top5_countries.index, top5_countries.values, color=DARK_RED)
ax.set_title("Top 5 Countries")

ax = fig.add_subplot(grid[2, 1])
audience_count = df["audience"].value_counts()
ax.bar(audience_count.index, audience_count.values,
       color=[AUDIENCE_COLORS.get(a, GREY) for a in audience_count.index])
ax.set_title("Audience Groups")
ax.tick_params(axis="x", rotation=25)

ax = fig.add_subplot(grid[2, 2])
top_ratings = df["rating"].value_counts().head(6).sort_values()
ax.barh(top_ratings.index, top_ratings.values, color=DARK_RED)
ax.set_title("Top Ratings")

save_dashboard(fig, "task6_dashboard1_overview.png", "Dashboard 1 - Executive Overview")

# ---------------------------------------------------------------------------
# Dashboard 2 - Content growth and strategy
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(14, 9))

ax = axes[0, 0]
years = added_by_type.index.astype(int)
ax.bar(years, added_by_type["Movie"], color=RED, label="Movie")
ax.bar(years, added_by_type["TV Show"], bottom=added_by_type["Movie"], color=WHITE, label="TV Show")
ax.set_title("Titles Added per Year (Movies and TV Shows)")
ax.set_xlabel("Year added")
ax.legend()

ax = axes[0, 1]
ax.plot(years, tv_share.values, marker="o", color=RED, linewidth=3)
ax.fill_between(years, tv_share.values, color=RED, alpha=0.15)
ax.set_title("Share of TV Shows in New Additions (%)")
ax.set_xlabel("Year added")
ax.grid(alpha=0.4)

ax = axes[1, 0]
month_names = [calendar.month_abbr[m] for m in month_counts.index]
colors = [RED if m == month_counts.idxmax() else DARK_RED for m in month_counts.index]
ax.bar(month_names, month_counts.values, color=colors)
ax.set_title("Which Month Gets the Most Additions?")
ax.set_ylabel("Titles (all years)")

ax = axes[1, 1]
ax.bar(age_by_year.index.astype(int), age_by_year.values, color=RED)
ax.set_title("Average Age of a Title When Added (years)")
ax.set_xlabel("Year added")

save_dashboard(fig, "task6_dashboard2_growth.png", "Dashboard 2 - Content Growth & Strategy")

# ---------------------------------------------------------------------------
# Dashboard 3 - Global reach and audience
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(14, 9))

ax = axes[0, 0]
top10_countries = country_count.head(10).sort_values()
colors = [DARK_RED] * len(top10_countries)
colors[-1] = RED
ax.barh(top10_countries.index, top10_countries.values, color=colors)
ax.set_title("Top 10 Countries")

ax = axes[0, 1]
ax.plot(non_us_by_year.index.astype(int), non_us_by_year.values, marker="o", color=RED, linewidth=3)
ax.fill_between(non_us_by_year.index.astype(int), non_us_by_year.values, color=RED, alpha=0.15)
ax.set_title("Titles NOT Led by the USA (%)")
ax.set_xlabel("Year added")
ax.grid(alpha=0.4)

ax = axes[1, 0]
audience_by_year.index = audience_by_year.index.astype(int)
audience_by_year.plot(kind="bar", stacked=True, ax=ax,
                      color=[AUDIENCE_COLORS.get(c, GREY) for c in audience_by_year.columns])
ax.set_title("Audience Mix by Year Added (%)")
ax.set_xlabel("")
ax.tick_params(axis="x", rotation=0)
ax.legend(fontsize=8, ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.12))

ax = axes[1, 1]
rating_by_type = pd.crosstab(df["rating"], df["type"])
rating_by_type = rating_by_type.loc[df["rating"].value_counts().head(8).index]
rating_by_type.plot(kind="bar", ax=ax,
                    color=[RED if c == "Movie" else WHITE for c in rating_by_type.columns])
ax.set_title("Top 8 Ratings: Movies vs TV Shows")
ax.set_xlabel("")
ax.tick_params(axis="x", rotation=45)

save_dashboard(fig, "task6_dashboard3_global_audience.png", "Dashboard 3 - Global Reach & Audience")

# ---------------------------------------------------------------------------
# Dashboard 4 - Genres and format
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(14, 9))

ax = axes[0, 0]
top10_genres = genre_count.head(10).sort_values()
colors = [DARK_RED] * len(top10_genres)
colors[-1] = RED
ax.barh(top10_genres.index, top10_genres.values, color=colors)
ax.set_title("Top 10 Genres")

ax = axes[0, 1]
line_colors = [RED, WHITE, GREY, "#B3B3B3", DARK_RED]
for genre, color in zip(genre_by_year.columns, line_colors):
    ax.plot(genre_by_year.index.astype(int), genre_by_year[genre], marker="o",
            linewidth=2, color=color, label=genre)
ax.set_title("Top 5 Genres Over Time (titles added)")
ax.set_xlabel("Year added")
ax.legend(fontsize=8)
ax.grid(alpha=0.4)

ax = axes[1, 0]
ax.hist(movies["duration_number"].dropna(), bins=30, color=RED, edgecolor=BLACK)
ax.set_title("How Long Are Movies? (minutes)")
ax.set_xlabel("Minutes")

ax = axes[1, 1]
seasons = shows["duration_number"].value_counts().sort_index().head(10)
ax.bar(seasons.index.astype(int).astype(str), seasons.values, color=RED)
ax.set_title("TV Shows by Number of Seasons")
ax.set_xlabel("Seasons")

save_dashboard(fig, "task6_dashboard4_genres_format.png", "Dashboard 4 - Genres & Format")

# ---------------------------------------------------------------------------
# Dashboard 5 - interactive (needs plotly, optional)
# ---------------------------------------------------------------------------
interactive_ok = False
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    fig = make_subplots(rows=2, cols=2, subplot_titles=(
        "Titles added per year", "Top 10 countries", "Top 10 genres", "Top ratings"))
    fig.add_trace(go.Bar(x=added_by_type.index, y=added_by_type["Movie"], name="Movie",
                         marker_color=RED), row=1, col=1)
    fig.add_trace(go.Bar(x=added_by_type.index, y=added_by_type["TV Show"], name="TV Show",
                         marker_color=WHITE), row=1, col=1)
    fig.add_trace(go.Bar(x=country_count.head(10).index, y=country_count.head(10).values,
                         marker_color=RED, showlegend=False), row=1, col=2)
    fig.add_trace(go.Bar(x=genre_count.head(10).index, y=genre_count.head(10).values,
                         marker_color=DARK_RED, showlegend=False), row=2, col=1)
    fig.add_trace(go.Bar(x=df["rating"].value_counts().head(8).index,
                         y=df["rating"].value_counts().head(8).values,
                         marker_color=GREY, showlegend=False), row=2, col=2)
    fig.update_layout(template="plotly_dark", barmode="stack", height=800,
                      title="Netflix Interactive Dashboard (hover, zoom and click the legend)")
    fig.write_html(OUTPUT_FOLDER / "task6_dashboard5_interactive.html")
    interactive_ok = True
    print("  Saved: task6_dashboard5_interactive.html")
except ImportError:
    print("  (Plotly is not installed, so the interactive dashboard was skipped.)")


# ===========================================================================
# STEP 4 - ACTIONABLE BUSINESS INSIGHTS
# ===========================================================================
banner("TASK 6 - STEP 4: Business insights")

insights = []


def add_insight(area, title, finding, action):
    """Keep one insight: where it applies, what we found, what to do."""
    insights.append({"area": area, "title": title, "finding": finding, "action": action})
    print(f"\n  [{area}] {title}\n    Found : {finding}\n    Action: {action}")


# --- 1. Catalogue growth ----------------------------------------------------
peak_year = int(added_per_year.idxmax())
latest_year = int(added_per_year.index.max())
latest_count = int(added_per_year.loc[latest_year])
peak_count = int(added_per_year.max())
vs_peak = latest_count / peak_count * 100
if vs_peak < 85 and latest_year != peak_year:
    growth_action = ("Check first whether the drop is real or only an incomplete year. If it is real, "
                     "focus the budget on fewer, higher-quality titles instead of adding volume.")
else:
    growth_action = "Additions are close to the peak, so keep the current pace and watch quality."
add_insight(
    "Content Strategy", "Catalogue growth over time",
    f"Most titles were added in {peak_year} ({peak_count:,}). The latest year in the data, "
    f"{latest_year}, has {latest_count:,} ({vs_peak:.0f}% of the peak; it may be a partial year).",
    growth_action)

# --- 2. Movies vs TV shows --------------------------------------------------
tv_first, tv_last = tv_share.iloc[0], tv_share.iloc[-1]
first_y, last_y = int(tv_share.index[0]), int(tv_share.index[-1])
if tv_last > tv_first:
    mix_action = ("TV shows are taking a bigger share of new titles. Series usually keep subscribers "
                  "coming back every week, so keep investing in them, especially returning series.")
else:
    mix_action = ("Movies are taking a bigger share of new titles. Plan a steady flow of series as "
                  "well, because they give viewers a reason to return.")
add_insight(
    "Content Strategy", "Movies and TV shows: how the mix moves",
    f"Movies are {len(movies) / len(df) * 100:.0f}% of the catalogue. The TV show share of new "
    f"additions went from {tv_first:.0f}% in {first_y} to {tv_last:.0f}% in {last_y}.",
    mix_action)

# --- 3. International content ----------------------------------------------
non_us_countries = country_count.drop("United States", errors="ignore")
top_non_us = non_us_countries.index[0]
intl_first, intl_last = non_us_by_year.iloc[0], non_us_by_year.iloc[-1]
add_insight(
    "Global Expansion", "Share of international content",
    f"{non_us_overall:.0f}% of titles are not led by the USA. This share moved from {intl_first:.0f}% "
    f"in {int(non_us_by_year.index[0])} to {intl_last:.0f}% in {int(non_us_by_year.index[-1])}. "
    f"{top_non_us} is the biggest non-US country with {int(non_us_countries.iloc[0]):,} titles.",
    f"Keep investing in local stories from the top non-US countries, starting with {top_non_us}. "
    f"Local titles can also be promoted to viewers in other countries.")

# --- 4. Audience ------------------------------------------------------------
audience_share = df["audience"].value_counts(normalize=True) * 100
rated = audience_share.drop("Not Rated", errors="ignore")
big_group, small_group = rated.index[0], rated.index[-1]
add_insight(
    "Audience", "Audience mix of the catalogue",
    f"{big_group} is the biggest group with {rated.iloc[0]:.0f}% of titles. "
    f"{small_group} is the smallest with {rated.iloc[-1]:.0f}%.",
    f"Look at the {small_group} group first. It has the fewest titles, so adding more could "
    f"reach viewers the catalogue serves less today. Check viewing data before investing.")

# --- 5. Genre concentration -------------------------------------------------
top3 = genre_count.head(3)
top3_share = top3.sum() / genre_count.sum() * 100
add_insight(
    "Programming", "How concentrated the genres are",
    f"The top 3 genres ({', '.join(top3.index)}) make up {top3_share:.0f}% of all genre tags. "
    f"The biggest is '{top3.index[0]}' with {int(top3.iloc[0]):,} titles.",
    "Keep the strong genres, and test smaller genres that match what viewers in growing "
    "countries ask for, so the catalogue does not depend on only a few genres.")

# --- 6. Freshness of the library --------------------------------------------
age_first, age_last = age_by_year.iloc[0], age_by_year.iloc[-1]
if age_last > age_first:
    age_action = ("Netflix adds older titles more often now. Licensed older content is cheap "
                  "filler, so balance it with new originals to keep the catalogue feeling fresh.")
else:
    age_action = ("New additions are getting fresher. Keep this focus on recent titles and use "
                  "older titles only to fill specific gaps.")
add_insight(
    "Content Strategy", "Age of titles when they are added",
    f"A title was on average {age_first:.1f} years old when added in {int(age_by_year.index[0])} "
    f"and {age_last:.1f} years old in {int(age_by_year.index[-1])}.",
    age_action)

# --- 7. Seasonality ---------------------------------------------------------
best_month = int(month_counts.idxmax())
low_month = int(month_counts.idxmin())
add_insight(
    "Release Planning", "Additions follow a monthly pattern",
    f"{calendar.month_name[best_month]} is the busiest month ({int(month_counts.max()):,} titles) "
    f"and {calendar.month_name[low_month]} is the quietest ({int(month_counts.min()):,}).",
    f"Plan big releases for {calendar.month_name[low_month]} and other quiet months, so viewers "
    f"have something new all year and big titles do not compete with each other.")

# --- 8. Duration and format -------------------------------------------------
median_movie = movies["duration_number"].median()
long_movie_share = (movies["duration_number"] > 120).mean() * 100
one_season_share = (shows["duration_number"] == 1).mean() * 100
if one_season_share >= 50:
    format_action = ("Many shows stop after one season. Look at why, since renewing the successful "
                     "ones is cheaper than starting new shows.")
else:
    format_action = ("Most shows continue beyond one season, so keep renewing the successful ones "
                     "and test shorter episodes or limited series for variety.")
add_insight(
    "Programming", "Movie length and show format",
    f"The middle movie runs {median_movie:.0f} minutes and {long_movie_share:.0f}% of movies are "
    f"longer than 2 hours. {one_season_share:.0f}% of TV shows have only one season.",
    format_action)

# --- 9. Data quality --------------------------------------------------------
missing_director = raw["director"].isna().mean() * 100
missing_country = raw["country"].isna().mean() * 100
add_insight(
    "Data Quality", "Missing information in the raw data",
    f"{missing_director:.0f}% of titles have no director and {missing_country:.0f}% have no country "
    f"in the original file.",
    "Make director and country required when titles are added. Better data gives better "
    "search, recommendations and reports.")

save_insights("task6", insights)


# ===========================================================================
# STEP 5 - THE EXECUTIVE REPORT (one responsive HTML page)
# ===========================================================================
banner("TASK 6 - STEP 5: Building the executive report")


def picture(file_name, caption):
    """Put a dashboard image inside the page (no extra files needed)."""
    data = base64.b64encode((OUTPUT_FOLDER / file_name).read_bytes()).decode()
    return (f'<figure><img src="data:image/png;base64,{data}" alt="{caption}" loading="lazy">'
            f"<figcaption>{caption}</figcaption></figure>")


def table_html(frame, with_index=False):
    """Turn a table into HTML that can scroll sideways on small phones."""
    return '<div class="table-wrap">' + frame.to_html(index=with_index, classes="data", border=0) + "</div>"


kpis = [
    (f"{len(df):,}", "Unique titles"),
    (f"{len(movies):,}", "Movies"),
    (f"{len(shows):,}", "TV Shows"),
    (f"{countries.nunique()}", "Countries"),
    (f"{genre_count.size}", "Genres"),
    (f"{non_us_overall:.0f}%", "Not led by USA"),
]
kpi_html = "".join(f'<div class="kpi"><div class="kpi-value">{v}</div><div>{t}</div></div>'
                   for v, t in kpis)

headline_html = "".join(f"<li><b>{html.escape(i['title'])}.</b> {html.escape(i['finding'])}</li>"
                        for i in insights[:3])

insight_cards = "".join(
    f'<article class="insight"><span class="tag">{html.escape(i["area"])}</span>'
    f'<h3>{n}. {html.escape(i["title"])}</h3>'
    f'<p><b>What we found:</b> {html.escape(i["finding"])}</p>'
    f'<p class="action"><b>What to do:</b> {html.escape(i["action"])}</p></article>'
    for n, i in enumerate(insights, start=1))

roadmap_html = "".join(f"<li><b>{html.escape(i['area'])}:</b> {html.escape(i['action'])}</li>"
                       for i in insights)

interactive_link = ""
if interactive_ok:
    interactive_link = ('<p><a class="btn" href="task6_dashboard5_interactive.html" target="_blank" '
                        'rel="noopener">Open the interactive dashboard</a></p>')

CSS = """
:root { --red:__RED__; --dark:__BLACK__; --text:__WHITE__; --card:#1f1f1f; --muted:#aaa; }
* { box-sizing:border-box; }
html { scroll-behavior:smooth; }
body { margin:0; font-family:'Segoe UI', Arial, sans-serif; background:var(--dark); color:var(--text); line-height:1.65; }
header { padding:56px 20px; text-align:center; background:linear-gradient(135deg,var(--red),var(--dark) 78%); }
header h1 { margin:0 0 8px; font-size:clamp(1.7rem, 5vw, 2.8rem); }
header p { margin:4px 0; }
nav { position:sticky; top:0; z-index:10; background:#000; display:flex; gap:6px; overflow-x:auto; padding:10px 14px; border-bottom:2px solid var(--red); }
nav a { color:var(--text); text-decoration:none; white-space:nowrap; padding:6px 12px; border-radius:20px; font-size:.92rem; }
nav a:hover { background:var(--red); }
main { max-width:1100px; margin:auto; padding:10px 16px 40px; }
section { background:#191919; border-radius:14px; padding:22px clamp(16px, 4vw, 30px); margin:26px 0; }
h2 { color:var(--red); margin-top:0; font-size:clamp(1.3rem, 3.5vw, 1.8rem); }
.kpis { display:grid; grid-template-columns:repeat(auto-fit, minmax(140px, 1fr)); gap:14px; margin:22px 0; }
.kpi { background:var(--card); border-left:5px solid var(--red); border-radius:10px; padding:14px; text-align:center; }
.kpi-value { font-size:1.8rem; font-weight:700; color:var(--red); }
.insights { display:grid; grid-template-columns:repeat(auto-fit, minmax(290px, 1fr)); gap:18px; }
.insight { background:var(--card); border-radius:12px; padding:18px; border-top:4px solid var(--red); }
.insight h3 { margin:10px 0; font-size:1.08rem; }
.tag { background:var(--red); font-size:.72rem; padding:3px 10px; border-radius:12px; text-transform:uppercase; letter-spacing:.5px; }
.action { background:#2a2a2a; padding:10px 12px; border-radius:8px; }
figure { margin:20px 0; text-align:center; }
img { max-width:100%; height:auto; border-radius:10px; }
figcaption { color:var(--muted); font-size:.9rem; }
.table-wrap { overflow-x:auto; margin:14px 0; }
table.data { border-collapse:collapse; width:100%; font-size:.92rem; }
table.data th, table.data td { padding:8px 12px; border-bottom:1px solid #333; text-align:left; white-space:nowrap; }
table.data th { background:#262626; color:var(--red); }
.btn { display:inline-block; background:var(--red); color:#fff; padding:10px 18px; border-radius:8px; text-decoration:none; }
li { margin:8px 0; }
footer { text-align:center; color:#999; padding:30px 16px; }
@media print { nav, .btn { display:none; } body { background:#fff; color:#000; } section, .insight, .kpi { background:#fff; border:1px solid #ccc; } }
""".replace("__RED__", RED).replace("__BLACK__", BLACK).replace("__WHITE__", WHITE)

page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Netflix Business Insights Report</title>
<style>{CSS}</style></head><body>

<header id="top">
  <h1>Netflix Business Insights Report</h1>
  <p>Executive report &middot; Data Analysis Using Python Internship &middot; Auspify Technologies</p>
  <p>By BENIMANA Theophile &middot; BenTech Rwanda</p>
</header>

<nav>
  <a href="#summary">Summary</a><a href="#eda">1. EDA</a><a href="#trends">2. Trends</a>
  <a href="#dashboards">3. Dashboards</a><a href="#insights">4. Insights</a>
  <a href="#roadmap">5. Next steps</a><a href="#method">Method</a>
</nav>

<main>
  <section id="summary">
    <h2>Executive Summary</h2>
    <p>This report studies the Netflix catalogue of {len(df):,} unique titles to find
    what the platform offers, how it is changing, and what the business can do next.</p>
    <div class="kpis">{kpi_html}</div>
    <h3>Top findings</h3>
    <ul>{headline_html}</ul>
  </section>

  <section id="eda">
    <h2>Step 1 - Exploratory Data Analysis</h2>
    <p>The original file has {len(raw):,} rows and {raw.shape[1]} columns. After cleaning,
    {len(df):,} unique titles remain. Missing values in the original file:</p>
    {table_html(column_summary)}
    <p>Summary of the main number columns after cleaning:</p>
    {table_html(numbers_summary, with_index=True)}
  </section>

  <section id="trends">
    <h2>Step 2 - Key Trends and Patterns</h2>
    <ul>
      <li>Most titles were added in <b>{peak_year}</b>.</li>
      <li>The TV show share of new additions moved from {tv_first:.0f}% to {tv_last:.0f}%.</li>
      <li>{non_us_overall:.0f}% of titles are not led by the USA.</li>
      <li>The busiest month for additions is <b>{calendar.month_name[best_month]}</b>.</li>
      <li>The top genre is <b>{html.escape(str(genre_count.index[0]))}</b>.</li>
    </ul>
  </section>

  <section id="dashboards">
    <h2>Step 3 - Dashboards</h2>
    {picture("task6_dashboard1_overview.png", "Dashboard 1 - Executive overview")}
    {picture("task6_dashboard2_growth.png", "Dashboard 2 - Content growth and strategy")}
    {picture("task6_dashboard3_global_audience.png", "Dashboard 3 - Global reach and audience")}
    {picture("task6_dashboard4_genres_format.png", "Dashboard 4 - Genres and format")}
    {interactive_link}
  </section>

  <section id="insights">
    <h2>Step 4 - Business Insights</h2>
    <div class="insights">{insight_cards}</div>
  </section>

  <section id="roadmap">
    <h2>Step 5 - Recommended Next Steps</h2>
    <ol>{roadmap_html}</ol>
  </section>

  <section id="method">
    <h2>Method and Limits</h2>
    <ul>
      <li>Data was cleaned in Task 1: duplicates removed, missing values filled, text standardized.</li>
      <li>A title with several countries or genres is counted once for each of them.</li>
      <li>The data describes the <b>catalogue</b>, not viewing hours, so the findings show what is offered,
      not what is most watched.</li>
      <li>The latest year may be incomplete. The findings show patterns and are not proof of cause.</li>
    </ul>
  </section>
</main>

<footer><a href="#top" style="color:#ccc">Back to top</a><br>
#Auspify #AuspifyTechnologies #AuspifyInternship #AuspifyProjects<br>
Made with Python, pandas and curiosity.</footer>
</body></html>"""

report_path = OUTPUT_FOLDER / "Netflix_Business_Insights_Report.html"
report_path.write_text(page, encoding="utf-8")

print("\nALL DONE! Open this file in your browser:")
print("  ", report_path)
