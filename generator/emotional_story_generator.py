"""
Emotional-Story Generator - har 2 hafte mein ek baar (Thursday, even ISO week)
chalta hai. Hot-take se format alag hai: yahan koi contrarian/debate nahi, sirf
warm/relatable "family + entrepreneur" universal connect hai.

ZAROORI (Ale ke sath decide kiya gaya): koi FABRICATED specific incident/kahani
nahi banayi jati, aur bachon ka naam kabhi use nahi hota. Sirf universal/honest
statements jo har entrepreneur-parent relate kar sake - isse trust genuine
rehta hai, kabhi "prove karo" wala risk nahi banta.
"""

import sys
import os
import json
import re
from datetime import datetime, timezone

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

SYSTEM_PROMPT = f"""Tum {config.BRAND_NAME} ke founder Ale ke personal LinkedIn ghost-writer ho.

Aaj ka post format "emotional/family-angle universal statement" hai - short-story broetry
style, jaisa entrepreneurs apni real zindagi ka honest reflection share karte hain.

BOHOT ZAROORI RULES (kabhi mat todna):
- Koi SPECIFIC fabricated incident/waqia mat banao (jaise "kal raat ko ye hua", "ek din mera beta...") -
  sirf UNIVERSAL/GENERAL truth likho jo har entrepreneur-parent relate kar sake
- Kisi bhi bachay ka naam, age, ya specific personal detail KABHI mat likho
- Jhooti/exaggerated tragedy ya struggle mat gadho - honest, general reflection hi likho
- Tone: warm, humble, thoda vulnerable, lekin sach - inspirational-fake nahi, relatable-honest

TOPIC ANGLE: Entrepreneur hone ke sath family zimmedari nibhana - raat der tak kaam,
subah zimmedariyan, "off day" na hona, phir bhi roz uthna aur apni family ke liye
better future banane ki koshish jari rakhna.

FORMAT (LinkedIn ke liye - "caption_linkedin" field):
- Chhoti lines, broetry style, one-sentence-per-line
- Universal observation se shuru karo (jaise "Raat ko der tak kaam khatam hota hai.\\nSubah zimmedariyan shuru ho jati hain.")
- Beech mein "koi course ye nahi sikhata" wala honest insight
- End: warm relatable question ("Kaun hai yahan jo dono cheezein sath sambhal raha hai?")
- 100-150 words

FORMAT (Instagram ke liye - "caption_instagram" field):
- 2-3 chhoti lines + relatable emoji + short CTA ("Tumhari kahani kya hai? 👇")
- 3-4 hashtags (jaise #EntrepreneurLife #WorkFamilyBalance #KreafyDigital)
- Max 50 words

IMAGE OVERLAY TEXT ("image_caption" field): 3-5 words, warm tone (jaise "STILL SHOWING UP DAILY")

Output STRICT JSON object mein do, kuch aur text ya explanation nahi:
{{
  "caption_linkedin": "...",
  "caption_instagram": "...",
  "image_caption": "..."
}}
"""


def _extract_json(text):
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"```\s*$", "", text)
    return text.strip()


def generate_with_gemini():
    import google.generativeai as genai

    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel(config.GEMINI_MODEL)
    response = model.generate_content(SYSTEM_PROMPT)
    return _extract_json(response.text)


def generate_with_claude():
    import anthropic

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=800,
        messages=[{"role": "user", "content": SYSTEM_PROMPT}],
    )
    return _extract_json(message.content[0].text)


def generate_emotional_post():
    engines = [config.PRIMARY_ENGINE, "claude" if config.PRIMARY_ENGINE == "gemini" else "gemini"]
    raw_output = None
    used_engine = None

    for engine in engines:
        try:
            print(f"Emotional-story post generate ho raha hai using: {engine}")
            raw_output = generate_with_gemini() if engine == "gemini" else generate_with_claude()
            used_engine = engine
            break
        except Exception as e:
            print(f"[WARN] {engine} fail ho gaya: {e}. Backup try ho raha hai...")
            continue

    if raw_output is None:
        raise RuntimeError("Dono engines (Gemini + Claude) fail ho gaye. API keys check karo.")

    post = json.loads(raw_output)
    post["photo_mood"] = "warm"  # ye format hamesha warm/smiling photo use karta hai, fixed

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "engine_used": used_engine,
        "post": post,
    }

    # Isay bhi hottake_post.json wale hi schema/path mein save karte hain taake
    # generate_hottake.js (image script) dono formats ke liye reusable rahe -
    # sirf caption fields ka set thoda alag hai (Twitter caption yahan nahi hota).
    out_path = os.path.join(config.OUTPUT_DIR, "hottake_post.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Emotional-story post generate ho gaya (mood: warm). Saved: {out_path}")
    return result


if __name__ == "__main__":
    generate_emotional_post()
