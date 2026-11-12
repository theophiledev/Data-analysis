# Netflix Content Analysis

Data Analysis Using Python Internship - Auspify Technologies
Author: BENIMANA Theophile - BenTech Rwanda

## Project structure

| File | Task |
|------|------|
| `task1_cleaning.py` | Task 1 - Data Cleaning & Preparation |
| `task3_country_analysis.py` | Task 3 - Country-Wise Content Analysis |
| `task4_trend_analysis.py` | Task 4 - Trend Analysis by Release Year |
| `task5_rating_genre.py` | Task 5 - Content Rating & Genre Analysis |
| `task6_business_insights.py` | Task 6 - Business Insights Report (EDA, 4 dashboards + interactive one, insights, executive report) |
| `build_report.py` | Builds the Tasks 1-5 report page |
| `common.py` | Shared colours, folders and helper functions |
| `run_all.py` | Runs everything in order |

## How to run

1. Install the libraries: `pip install -r requirements.txt`
2. Copy the Netflix dataset into this folder and name it `netflix_titles.csv`
3. Run everything: `python run_all.py`
   (or run each task alone, starting with `task1_cleaning.py`)
4. Open `output/Netflix_Report.html` (Tasks 1-5) and `output/Netflix_Business_Insights_Report.html` (Task 6) in your browser

## Output (created in the `output` folder)

- `netflix_cleaned.csv` - cleaned data (Task 1)
- `task3_*.png`, `task4_*.png`, `task5_*.png` - charts
- `task5_interactive_genre_audience.html` - interactive chart
- `Netflix_Report.html` - report page for Tasks 1-5
- `task6_dashboard1..4_*.png` and `task6_dashboard5_interactive.html` - Task 6 dashboards
- `Netflix_Business_Insights_Report.html` - Task 6 executive report
  ### VISIT THIS URL FOR REPORT AND RESULT SUMMARY DATA ANLAYISED
  `https://theophiledev.github.io/Data-analysis/output/Netflix_Business_Insights_Report.html`
