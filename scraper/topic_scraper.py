"""
Topic Input - Google Trends automated hai (koi restriction nahi).
Reddit automated NAHI hai (Reddit ki Responsible Builder Policy commercial
AI-content-generation ke liye automated scraping allow nahi karti - jaisa
pehle discuss kiya). Iski jagah: Ale hafte mein 15-20 min manually Reddit
browse karke acha material `manual_topics.txt` file mein paste kar deta hai,
content_generator wahan se bhi padh leta hai.
"""

import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config


def read_manual_topics():
    """Ale ne jo hafte mein manually Reddit se copy-paste kiya hai, wo yahan se padhta hai.
    PEHLE Google Doc try karta hai (phone se easily editable), fail ho to local
    manual_topics.txt fallback. Dono khali/nahi to empty list - system tab sirf
    Google Trends pe chalega, rukega nahi."""

    # 1. Google Doc try karo (agar service account configured hai)
    if config.GOOGLE_SERVICE_ACCOUNT_JSON and config.GOOGLE_DOC_ID:
        try:
            lines = read_google_doc_topics()
            if lines:
                print(f"Google Doc se {len(lines)} topics mil gaye.")
                return lines
        except Exception as e:
            print(f"[WARN] Google Doc padhne mein masla: {e}. Local file try ho raha hai...")

    # 2. Local manual_topics.txt fallback
    manual_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "manual_topics.txt")
    if not os.path.exists(manual_path):
        return []

    with open(manual_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip() and not line.strip().startswith("#")]
    return lines


def read_google_doc_topics():
    """Google Drive service account se 'Weekly Topics' Doc ka plain text nikalta hai."""
    import json
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    import io
    from googleapiclient.http import MediaIoBaseDownload

    creds_info = json.loads(config.GOOGLE_SERVICE_ACCOUNT_JSON)
    creds = service_account.Credentials.from_service_account_info(
        creds_info, scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    service = build("drive", "v3", credentials=creds)

    request = service.files().export_media(fileId=config.GOOGLE_DOC_ID, mimeType="text/plain")
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()

    text = buffer.getvalue().decode("utf-8")
    lines = [
        line.strip() for line in text.splitlines()
        if line.strip() and not line.strip().startswith("#") and not line.strip().startswith("---")
        and not line.strip().startswith("Yahan") and not line.strip().startswith("Example")
        and not line.strip().startswith("Jab bhi") and not line.strip().startswith("(Neeche")
        and "developer quoted 480 hours" not in line.lower()  # sample line skip karo
        and "3 years, an agency held" not in line.lower()      # sample line skip karo
    ]
    return lines


def scrape_google_trends(keywords=None):
    """Google Trends se related/rising queries nikalta hai. Free, koi API key nahi chahiye."""
    from pytrends.request import TrendReq

    if keywords is None:
        keywords = ["AI automation business", "no-code app development", "web development agency"]

    pytrends = TrendReq(hl="en-US", tz=360)
    trends_data = []

    for kw in keywords:
        try:
            pytrends.build_payload([kw], timeframe="now 7-d")
            related = pytrends.related_queries()
            rising = related.get(kw, {}).get("rising")
            if rising is not None:
                for _, row in rising.iterrows():
                    trends_data.append({
                        "source": "google_trends",
                        "seed_keyword": kw,
                        "query": row["query"],
                        "value": row["value"],
                    })
        except Exception as e:
            print(f"[WARN] Google Trends keyword '{kw}' skip ho gaya: {e}")
            continue

    return trends_data


def collect_all_topics():
    """Google Trends (automated) + manual_topics.txt (Ale ka weekly curation) - dono se topics collect karke JSON mein save karta hai."""
    print("Manual topics file padhi ja rahi hai (agar hai)...")
    manual_topics = read_manual_topics()

    print("Google Trends se topics scrape ho rahe hain...")
    trends_topics = scrape_google_trends()

    all_topics = {
        "generated_at": datetime.utcnow().isoformat(),
        "manual_topics": manual_topics,
        "trends_topics": trends_topics,
    }

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(config.OUTPUT_DIR, "topics.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_topics, f, indent=2, ensure_ascii=False)

    print(f"Total topics collected: {len(manual_topics)} Manual + {len(trends_topics)} Trends")
    print(f"Saved to: {out_path}")
    return all_topics


if __name__ == "__main__":
    collect_all_topics()
