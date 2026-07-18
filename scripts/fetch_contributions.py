#!/usr/bin/env python3
"""Fetch a public GitHub contribution calendar (no token required) and
write data/contributions.json with raw days + derived stats."""
import json
import sys
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "wairiukoirwine"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"


def fetch_days():
    resp = requests.get(URL, headers={"User-Agent": "profile-art-bot"}, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    days = []
    # GitHub renders each day as either a <td> (older markup) or
    # <table> ... <tool-tip>/<td class="ContributionCalendar-day">.
    for cell in soup.select("td.ContributionCalendar-day"):
        d = cell.get("data-date")
        level = cell.get("data-level")
        if d is None or level is None:
            continue
        days.append({"date": d, "level": int(level)})

    if not days:
        raise RuntimeError(
            "No contribution cells found — GitHub markup may have changed, "
            "or the profile could be private."
        )

    days.sort(key=lambda x: x["date"])
    return days


def derive_stats(days):
    counts = {d["date"]: d["level"] for d in days}
    total_active = sum(1 for d in days if d["level"] > 0)

    # streaks (based on active days, level > 0)
    longest = current = 0
    running = 0
    today_str = date.today().isoformat()
    for d in days:
        if d["level"] > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0
    # current streak: walk backward from the last day with data
    running = 0
    for d in reversed(days):
        if d["level"] > 0:
            running += 1
        else:
            break
    current = running

    best_day = max(days, key=lambda d: d["level"])
    monthly = {}
    for d in days:
        month = d["date"][:7]
        monthly[month] = monthly.get(month, 0) + (1 if d["level"] > 0 else 0)

    return {
        "total_active_days": total_active,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best_day["date"],
        "monthly_active_days": monthly,
        "generated": today_str,
    }


def main():
    days = fetch_days()
    stats = derive_stats(days)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"days": days, "stats": stats}, indent=2))
    print(f"Wrote {OUT} — {len(days)} days, current streak {stats['current_streak']}")


if __name__ == "__main__":
    main()
