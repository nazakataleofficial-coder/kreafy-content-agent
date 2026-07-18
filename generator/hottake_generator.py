"""
Hot-Take Generator - carousel se bilkul alag format: EK real-face photo + EK bold
"broetry" style opinion post (jaisa LinkedIn ke top personal-brand creators
likhte hain - Hafiz Basit Ali jaisa). Carousel "story" hai, ye "opinion/authority"
hai - dono ka role alag hai isliye format bhi jaan-bujh kar alag rakha gaya hai.

Har run mein SIRF EK hot-take post banta hai (carousel ki tarah 5 nahi) - ye format
high-exposure (real chehra) hai isliye rare/special rakha gaya hai (README ke
day-of-week schedule ke mutabiq hafte mein 3 din hi chalega).
"""

import sys
import os
import json
import re
from datetime import datetime, timezone

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

# 10 fixed business-angle niches - Kreafy ke actual services/positioning se seedha juri
# hui hain (random opinion nahi). Ek din mein isi list se ek (rotating) angle use hota hai.
NICHES = [
    {"id": "pricing_value", "angle": "Cheap clients vs fair pricing - kyun sasta client sabse zyada complain karta hai"},
    {"id": "freelancer_vs_agency", "angle": "Solo freelancer ke risks vs agency ki reliability (deadline/scale/backup)"},
    {"id": "ai_automation_myth", "angle": "'AI se sab free/instant ho jayega' wale myth ko bust karna - real automation setup vs hype"},
    {"id": "speed_vs_quality", "angle": "Traditional agencies ka slow bloated process vs fast-but-still-quality delivery"},
    {"id": "content_automation_myth", "angle": "Faceless/passive-income YouTube automation myths vs asal consistency-based growth"},
    {"id": "client_red_flags", "angle": "Kaunse clients loss hote hain - deadline disrespect, scope-creep, chronic negotiation"},
    {"id": "work_ethic", "angle": "Silent consistent work vs loud announcing - discipline ka asal matlab"},
    {"id": "cheap_vs_premium", "angle": "'Sasta kaam' ka trap - premium positioning kyun zyada tikta hai long-term"},
    {"id": "deadline_commitment", "angle": "Time pe deliver na karne wale agencies ki reputation kaise chupke se bigadti hai"},
    {"id": "nocode_myth", "angle": "'Coding nahi aati to app nahi ban sakta' jaisa myth bust karna (vibe-coding/no-code angle)"},
]

# Real photo ka mood - konsa niche/tone kis expression se best match karta hai.
# Gemini ko yehi fixed list di jati hai taake wo hamesha in 6 mein se EK chune
# (asset filenames se seedha match karta hai - assets/real_photos/<mood>.png)
PHOTO_MOODS = ["confident", "stern", "thoughtful", "warm", "casual", "determined"]

SYSTEM_PROMPT = f"""Tum {config.BRAND_NAME} ke founder Ale ke personal LinkedIn ghost-writer ho,
"broetry" style ke expert - jaisa top personal-brand creators (jaise Hafiz Basit Ali, Justin Welsh)
likhte hain: chhoti chhoti lines, white space, contrarian opening, rule-of-three, credibility proof,
polarizing ending.

Brand niche: {config.BRAND_NICHE}
Is post ka topic/angle: {{niche_angle}}

ZAROORI RULES:
- Koi religion, politics, ya kisi real teesre insaan/company ka naam mat lo - sirf business/professional opinion
- Confident, thoda provocative, lekin professional rahe - hate/insult nahi, sirf contrarian truth
- Real Kreafy positioning se match kare (high-ticket, quality-first, no race-to-bottom pricing)

FORMAT (LinkedIn ke liye - "caption_linkedin" field):
- Opener: 2-line contrast statement (jaise "X hamesha Y hota hai.\\n\\nZ nahi.") YA bold claim ek line mein
- Beech mein: bohot chhoti lines, one-sentence-per-line, "rule of three" pattern (3 cheezein "Not X. Not Y. Not Z." wala)
- Kreafy ka apna experience/rule ka zikar karo ek line mein (proof/credibility)
- Ending: polarizing question ya "A ya B, tum kaun ho" wala choice, phir "Agree or not. Drop it below 👇"
- Har important phrase ko **do asterisks** ke beech mein likho (isay bold unicode banaya jayega baad mein)
- 120-180 words total

FORMAT (Twitter ke liye - "caption_twitter" field):
- SIRF 3-4 lines, STRICT 200-250 characters total
- Hook line + core insight line + short CTA line
- Koi bold marker nahi, seedha plain punchy text

FORMAT (Instagram ke liye - "caption_instagram" field):
- 1 punchy opener line + 1 short supporting line
- Phir 4 relevant hashtags (niche-specific, jaise carousel wale)
- Short CTA ("Agree? Comment below 👇")
- STRICT max 60 words total (Instagram caption ke "more" ke peeche chhup jane se bachne ke liye)

IMAGE OVERLAY TEXT ("image_caption" field):
- SIRF 2-4 words, ALL CAPS, jo real-photo pe bold overlay ki tarah lage (jaise "CHEAP CLIENTS COST MORE")
- Poore post ka sabse punchy nichod, ek nazar mein samajh aaye

PHOTO MOOD ("photo_mood" field):
- In FIXED options mein se EK chuno (bilkul yehi spelling): {', '.join(PHOTO_MOODS)}
- "confident" = seedha strong stance, "stern" = challenging/confrontational tone,
  "thoughtful" = reflective/wisdom angle, "warm" = friendly relatable advice,
  "casual" = light/relatable observation, "determined" = discipline/grind angle

Output STRICT JSON object mein do, kuch aur text ya explanation nahi:
{{{{
  "niche_id": "...",
  "caption_linkedin": "...",
  "caption_twitter": "...",
  "caption_instagram": "...",
  "image_caption": "...",
  "photo_mood": "..."
}}}}
"""


def _extract_json(text):
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"```\s*$", "", text)
    return text.strip()


def _pick_niche_for_today():
    """Day-of-year ke hisaab se 10 niches mein rotate karta hai - taake har baar
    alag angle mile, koi ek niche baar baar jaldi repeat na ho."""
    day_index = datetime.now(timezone.utc).timetuple().tm_yday
    return NICHES[day_index % len(NICHES)]


def generate_with_gemini(prompt_text):
    import google.generativeai as genai

    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel(config.GEMINI_MODEL)
    response = model.generate_content(prompt_text)
    return _extract_json(response.text)


def generate_with_claude(prompt_text):
    import anthropic

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=1200,
        messages=[{"role": "user", "content": prompt_text}],
    )
    return _extract_json(message.content[0].text)


def generate_hottake_post():
    niche = _pick_niche_for_today()
    prompt_text = SYSTEM_PROMPT.format(niche_angle=niche["angle"])

    engines = [config.PRIMARY_ENGINE, "claude" if config.PRIMARY_ENGINE == "gemini" else "gemini"]
    raw_output = None
    used_engine = None

    for engine in engines:
        try:
            print(f"Hot-take generate ho raha hai using: {engine} (niche: {niche['id']})")
            raw_output = generate_with_gemini(prompt_text) if engine == "gemini" else generate_with_claude(prompt_text)
            used_engine = engine
            break
        except Exception as e:
            print(f"[WARN] {engine} fail ho gaya: {e}. Backup try ho raha hai...")
            continue

    if raw_output is None:
        raise RuntimeError("Dono engines (Gemini + Claude) fail ho gaye. API keys check karo.")

    post = json.loads(raw_output)
    post["niche_id"] = niche["id"]

    if post.get("photo_mood") not in PHOTO_MOODS:
        post["photo_mood"] = "confident"  # safe default agar model ne invalid mood diya ho

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "engine_used": used_engine,
        "post": post,
    }

    out_path = os.path.join(config.OUTPUT_DIR, "hottake_post.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Hot-take post generate ho gaya (niche: {niche['id']}, mood: {post['photo_mood']}). Saved: {out_path}")
    return result


if __name__ == "__main__":
    generate_hottake_post()
