"""
Daily Scheduler - decide karta hai aaj konsa format(s) chalega aur kaunse platforms pe.
GitHub Actions workflow isi file ke output (output/schedule.json) ko padh ke
apne steps conditionally chalata/skip karta hai (`if:` conditions).

Agreed weekly plan (Ale ke sath discuss kiya hua):
- Mon, Wed, Sat  -> Carousel        (LinkedIn, Twitter, Instagram)
- Tue, Fri       -> Hot-take        (LinkedIn, Twitter, Instagram)
- Sun            -> Hot-take        (Twitter, Instagram only - LinkedIn Sunday weak din hai)
- Thu            -> Bi-weekly: EVEN ISO week = Emotional-story (LinkedIn, Instagram)
                     ODD ISO week  = Carousel (LinkedIn, Twitter, Instagram)

Facebook hamesha OFF hai (high-ticket international audience goal se match nahi karta -
sirf Instagram Business linkage ke liye Page silently bana rakhna kaafi hai, active post nahi).
"""

import os
import json
from datetime import datetime, timezone

from config import config

ALL_PLATFORMS = ["linkedin", "twitter", "instagram"]
NO_LINKEDIN = ["twitter", "instagram"]


def build_today_schedule():
    now = datetime.now(timezone.utc)
    weekday = now.weekday()  # Monday=0 ... Sunday=6
    iso_week = now.isocalendar()[1]

    schedule = {
        "date": now.strftime("%Y-%m-%d"),
        "weekday": weekday,
        "run_carousel": False,
        "run_hottake": False,
        "run_emotional": False,
        "platforms": [],
    }

    if weekday in (0, 2, 5):  # Mon, Wed, Sat
        schedule["run_carousel"] = True
        schedule["platforms"] = ALL_PLATFORMS

    elif weekday in (1, 4):  # Tue, Fri
        schedule["run_hottake"] = True
        schedule["platforms"] = ALL_PLATFORMS

    elif weekday == 6:  # Sunday
        schedule["run_hottake"] = True
        schedule["platforms"] = NO_LINKEDIN

    elif weekday == 3:  # Thursday - bi-weekly
        if iso_week % 2 == 0:
            schedule["run_emotional"] = True
            schedule["platforms"] = ["linkedin", "instagram"]
        else:
            schedule["run_carousel"] = True
            schedule["platforms"] = ALL_PLATFORMS

    return schedule


def main():
    schedule = build_today_schedule()
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(config.OUTPUT_DIR, "schedule.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(schedule, f, indent=2)

    print(f"Aaj ({schedule['date']}, weekday={schedule['weekday']}) ka schedule:")
    print(json.dumps(schedule, indent=2))

    # GitHub Actions ke liye GITHUB_OUTPUT mein bhi likh do taake workflow steps
    # `if:` condition mein seedha use kar sakein (extra JSON-parse step ki zarurat nahi)
    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a", encoding="utf-8") as f:
            f.write(f"run_carousel={str(schedule['run_carousel']).lower()}\n")
            f.write(f"run_hottake={str(schedule['run_hottake']).lower()}\n")
            f.write(f"run_emotional={str(schedule['run_emotional']).lower()}\n")
            f.write(f"platforms={','.join(schedule['platforms'])}\n")


if __name__ == "__main__":
    main()
