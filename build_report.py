"""
build_report.py - builds one HTML report page from the results of all tasks.

Author: BENIMANA Theophile - BenTech Rwanda

Run the task files first, then:  python build_report.py
Then double-click output/Netflix_Report.html
"""

import base64
import html

from common import (RED, WHITE, BLACK, OUTPUT_FOLDER, banner,
                    load_cleaned, load_insights, split_values)

banner("Building your report page")

df = load_cleaned()
movies = df[df["type"] == "Movie"]
shows = df[df["type"] == "TV Show"]
countries = split_values(df["country"])
countries = countries[countries != "Unknown"]


def picture(file_name, caption):
    """Put a chart image inside the HTML page (no extra files needed)."""
    path = OUTPUT_FOLDER / file_name
    if not path.exists():
        return ""
    data = base64.b64encode(path.read_bytes()).decode()
    return (f'<figure><img src="data:image/png;base64,{data}" alt="{caption}">'
            f"<figcaption>{caption}</figcaption></figure>")


def bullet_list(task_name):
    """Turn the saved findings of a task into an HTML list."""
    items = load_insights(task_name)
    return "<ul>" + "".join(f"<li>{html.escape(s)}</li>" for s in items) + "</ul>"


# ---------------------------------------------------------------------------
# Fun facts
# ---------------------------------------------------------------------------
fun_facts = []

if movies["duration_number"].notna().any():
    longest = movies.loc[movies["duration_number"].idxmax()]
    fun_facts.append(f"Longest movie: <b>{html.escape(str(longest['title']))}</b> "
                     f"({int(longest['duration_number'])} minutes).")

if shows["duration_number"].notna().any():
    biggest = shows.loc[shows["duration_number"].idxmax()]
    fun_facts.append(f"TV show with the most seasons: <b>{html.escape(str(biggest['title']))}</b> "
                     f"({int(biggest['duration_number'])} seasons).")

directors = split_values(df[df["director"] != "Unknown"]["director"])
if len(directors) > 0:
    top_director = directors.value_counts()
    fun_facts.append(f"Director with the most titles: <b>{html.escape(str(top_director.index[0]))}</b> "
                     f"({top_director.iloc[0]} titles).")

oldest = df.loc[df["release_year"].idxmin()]
fun_facts.append(f"Oldest title: <b>{html.escape(str(oldest['title']))}</b> "
                 f"(released in {int(oldest['release_year'])}).")

# ---------------------------------------------------------------------------
# Top cards
# ---------------------------------------------------------------------------
cards = [
    (f"{len(df):,}", "Titles analysed"),
    (f"{len(movies):,}", "Movies"),
    (f"{len(shows):,}", "TV Shows"),
    (f"{countries.nunique()}", "Countries"),
    (f"{int(df['release_year'].min())}-{int(df['release_year'].max())}", "Years covered"),
]
cards_html = "".join(f'<div class="card"><div class="big">{n}</div><div>{t}</div></div>'
                     for n, t in cards)
facts_html = "".join(f"<li>{f}</li>" for f in fun_facts)

interactive_link = ""
if (OUTPUT_FOLDER / "task5_interactive_genre_audience.html").exists():
    interactive_link = ('<p><a class="btn" href="task5_interactive_genre_audience.html" '
                        'target="_blank">Open the interactive genre chart</a></p>')

# ---------------------------------------------------------------------------
# The page
# ---------------------------------------------------------------------------
page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Netflix Content Story</title>
<style>
  body {{ margin:0; font-family:Segoe UI, Arial, sans-serif; background:{BLACK}; color:{WHITE}; line-height:1.6; }}
  header {{ padding:50px 20px; text-align:center; background:linear-gradient(135deg,{RED},{BLACK} 75%); }}
  header h1 {{ margin:0; font-size:2.4em; }}
  main {{ max-width:1000px; margin:auto; padding:20px; }}
  .cards {{ display:flex; flex-wrap:wrap; gap:14px; justify-content:center; margin:25px 0; }}
  .card {{ background:#222; border-left:5px solid {RED}; border-radius:10px; padding:16px 22px; min-width:140px; text-align:center; }}
  .big {{ font-size:1.8em; font-weight:bold; color:{RED}; }}
  section {{ background:#1d1d1d; border-radius:14px; padding:20px 26px; margin:26px 0; }}
  h2 {{ color:{RED}; margin-top:0; }}
  figure {{ margin:18px 0; text-align:center; }}
  img {{ max-width:100%; border-radius:10px; }}
  figcaption {{ color:#aaa; font-size:.9em; }}
  li {{ margin:6px 0; }}
  .btn {{ background:{RED}; color:white; padding:10px 18px; border-radius:8px; text-decoration:none; }}
  footer {{ text-align:center; color:#999; padding:30px; }}
</style></head><body>
<header>
  <h1>The Netflix Content Story</h1>
  <p>Data Analysis Using Python Internship &middot; Auspify Technologies</p>
  <p>By BENIMANA Theophile &middot; BenTech Rwanda</p>
</header>
<main>
  <div class="cards">{cards_html}</div>

  <section><h2>Fun facts</h2><ul>{facts_html}</ul></section>

  <section><h2>Task 1 - Data Cleaning &amp; Preparation</h2>
    <p>I cleaned the file step by step and created new columns to make the next tasks easier.</p>
    {bullet_list("task1")}
  </section>

  <section><h2>Task 3 - Country-Wise Analysis</h2>
    {picture("task3_top10_countries.png", "Top 10 countries behind Netflix titles")}
    {picture("task3_international_share.png", "Share of titles not led by the USA")}
    {bullet_list("task3")}
  </section>

  <section><h2>Task 4 - Trend Analysis by Release Year</h2>
    {picture("task4_titles_by_release_year.png", "Titles by release year")}
    {picture("task4_content_age.png", "Average age of content when added")}
    {bullet_list("task4")}
  </section>

  <section><h2>Task 5 - Rating &amp; Genre Analysis</h2>
    {picture("task5_rating_by_type.png", "Ratings for Movies and TV Shows")}
    {picture("task5_audience_donut.png", "Audience groups")}
    {interactive_link}
    {bullet_list("task5")}
  </section>
</main>
<footer>#Auspify #AuspifyTechnologies #AuspifyInternship #AuspifyProjects<br>Made with Python, pandas and curiosity.</footer>
</body></html>"""

report_path = OUTPUT_FOLDER / "Netflix_Report.html"
report_path.write_text(page, encoding="utf-8")

print("\nALL DONE! Open this file in your browser:")
print("  ", report_path)
