"""
run_all.py - runs every task in the right order, then builds the report.

Author: BENIMANA Theophile - BenTech Rwanda

Run:  python run_all.py
(You can also run each task file alone, but task1_cleaning.py must be first.)
"""

import subprocess
import sys
from pathlib import Path

folder = Path(__file__).parent

steps = [
    "task1_cleaning.py",
    "task3_country_analysis.py",
    "task4_trend_analysis.py",
    "task5_rating_genre.py",
    "task6_business_insights.py",
    "build_report.py",
]

for step in steps:
    print(f"\n>>> Running {step}")
    result = subprocess.run([sys.executable, str(folder / step)])
    if result.returncode != 0:
        print(f"\nStopped: {step} had a problem. Fix it and run again.")
        sys.exit(1)
