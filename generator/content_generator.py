"""
Content Generator - topics.json se raw topics leke roz N unique posts
banata hai (hook-story-conflict-twist-CTA style, Ale ka preferred format).

Dual-engine: Primary = Gemini (free), Backup = Claude (agar Claude Code
subscription available ho). Agar ek fail ho to dusra automatically try hota hai -
is tarah system kabhi kisi ek subscription pe depend nahi karta.
"""

import sys
import os
import json
import re
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config


def _build_rotation_block():
    lines = []
    for slot in config.SERVICE_ROTATION:
        lines.append(f"Slot {slot['slot']} -> Service: {slot['service']} | Angle: {slot['angle']}")
    return "\n".join(lines)


SYSTEM_PROMPT = f"""Tum {config.BRAND_NAME} ke liye ek senior direct-response copywriter ho,
jisne high-ticket agencies ke liye scroll-stopping social content likha hai.

Brand niche: {config.BRAND_NICHE}
Brand voice: {config.BRAND_VOICE}
Goal: high-paying clients attract karna (web dev, app dev, YouTube automation, animation) - cheap/low-ticket
audience nahi chahiye, isliye tone hamesha premium/confident rakho, discount-selling wala tone kabhi nahi.

LANGUAGE RULE (bohot zaroori):
- Itni simple wording likho ke ek 7 saal ka bachcha bhi samajh jaye
- Har sentence chhota rakho (max 8-10 words)
- Mushkil/heavy English words mat use karo (jaise "leverage", "synergy", "optimize" - inki jagah simple lafz: "use karo", "behtar banao")
- Simple hone ka matlab childish nahi - tone hamesha confident aur professional rahe, sirf lafz aasan hon

SERVICE ROTATION - har din is exact order mein 5 posts banao, har slot apni service pe focused ho:
{_build_rotation_block()}

HOOK RULES (pehli line, caption ka sabse zaroori hissa - in patterns mein se use karo):
- Concrete number/shock stat se shuru ("Rs 5 lac", "10 din", "3 mahine ki jagah 2 hafte")
- Contrarian/pattern-interrupt statement ("Traditional agencies ye kabhi nahi bataengi...")
- Direct relatable question jo target client khud se poochta hai
- "Most business owners don't know..." wala open-loop/curiosity hook
- Kabhi bhi generic greeting ya "Hi guys" se shuru mat karo

CAPTION STRUCTURE: Har platform ki caption mein bhi (chhoti ho ya lambi) ye poora arc hona chahiye -
Hook -> Pain point/Story -> Solution -> CTA. Sirf lambai alag hai, structure hamesha wahi.

PLATFORM-SPECIFIC CAPTIONS (bohot zaroori - teeno alag hain, ek jaisi mat likho):
1. "caption_linkedin" - English, 60-100 words. Professional, detailed story arc (Hook->Pain->Story->Solution->CTA).
   LinkedIn ka audience global/US/UK/ME hai, thoda detail sahenge.
2. "caption_facebook" - Roman Urdu (Hinglish/Urdu mix), STRICT 40-50 words. Compressed version -
   hook + pain point + chhoti story + CTA, lekin sirf 40-50 words mein. Pakistani local audience.
3. "caption_twitter" - English, STRICT 20-30 words. Bohot tight - hook + pain point + CTA
   (story wala hissa chhod sakte ho agar jagah na ho, lekin hook-pain-CTA teeno zaroor hon).
   X/Twitter ka audience bohot jaldi scroll karta hai, isliye ye sabse compressed honi chahiye.

Teeno mein SAME core story/numbers/facts hon (jaisa ek hi ghatna teen alag logon ko teen alag
lambai mein sunana), sirf lambai aur thoda tone platform ke hisaab se badle - kabhi bhi ek
ko doosre ka seedha translation mat banao, har ek apni jagah par naturally likhi honi chahiye.

CAROUSEL STRUCTURE (ye single image NAHI - minimum 4-slide swipeable carousel hai):
Har post ke liye "carousel_slides_en" aur "carousel_slides_ur" dono arrays banao, har ek exactly 4 slides, is structure mein:
1. Slide 1 (HOOK): STRICT max 10 words - 2026 research kehta hai reader sirf 2-3 second dekhta hai, itni lambi hook chalti nahi jitni bhi choti ho utna behtar. Real number/scenario ke sath, attention pakadne wala.
2. Slide 2 (PROBLEM): 1-2 chhote sentences (max 20-25 words) jo poori problem ki story sunayein - kya hua, kyun masla hai
3. Slide 3 (SOLUTION): 1-2 chhote sentences (max 20-25 words) jo Kreafy ka solution/result poori tarah samjhayein - specific detail ke sath
4. Slide 4 (CTA): Alag-alag type ka CTA rotate karo (algorithm engagement signals ke liye zaroori hai):
   - Comment-bait question (jaise "Which mistake have you made?") - comments algorithm ko sabse zyada signal dete hain
   - Ya direct action ("DM 'START' for a free audit")
   - Kabhi kabhi "Save this for later" wala cue bhi add karo (2026 mein saves sabse bada engagement signal hain, likes se zyada)

Zaroori: Ye 4 slides mil ke ek chhoti si complete story honi chahiye - koi bhi in 4 slides ko padh ke poori
baat samajh jaye, bina caption padhe. Real detail/numbers/scenario do, generic mat likho.

HIGHLIGHT MARKER: Har slide ke text mein EK sabse zaroori word/phrase ko **do asterisks** ke beech mein likho
(jaise "**$400** mein poora business platform"). Ye word carousel image mein ek colored box mein highlight hoga -
isliye number, price, ya sabse punchy word ko hi marker do, poore sentence ko nahi.

ILLUSTRATION EMOTION: Har post ke liye "illustration_emotion" field bhi do - is story ke sabse zaroori
emotion/moment ko in FIXED options mein se EK chuno (bilkul yehi spelling use karo, kuch aur mat likho):
"shocked", "confident", "thinking", "explaining", "celebrating"
(story ke hisaab se sabse fit wala chuno - jaise koi bade number/price wali baat ho to "shocked",
solution/result wala moment ho to "confident" ya "celebrating")

HASHTAGS: Har post ke liye "hashtags" bhi do - ek array of 5 relevant, specific hashtags (generic
#business #success jaisi weak hashtags NAHI - service-specific aur niche-relevant hon, jaise
#WebDevelopment #NextJS #StartupTools #AIAutomation #PakistanTech waghera, jo us post ke slot/service
ke hisaab se badlein). Har platform apni zaroorat ke hisaab se in mein se kuch use karega.

Rules:
- Har post apne slot ki service pe hi focused rahe, mix mat karo
- Koi generic "5 tips" wala post NAHI - hamesha specific/concrete, real numbers/scenarios ke sath
- Output STRICT JSON array format mein do, kuch aur text ya explanation nahi

EXAMPLE (isi quality/style ka target rakho - real number, real detail, koi generic baat nahi):
{{
  "slot": 1,
  "service": "Web Development",
  "caption_linkedin": "A developer quoted 480 hours of work. Client's budget was $400. Every reply on the thread said the same thing: that's below minimum wage. Real software costs real money. We don't cut corners - we quote fair rates from day one. What's your project actually worth?",
  "caption_facebook": "Ek developer ne 480 ghante ka kaam quote kiya. Client ka budget sirf $400 tha - internet ne kaha ye minimum wage se kam hai. Hum aise corners nahi kaatte. Din 1 se fair rate dete hain. Tumhare project ki asal keemat kya hai?",
  "caption_twitter": "480 hours quoted. Client offered $400. That's below minimum wage. We quote fair rates from day one. What's your project actually worth?",
  "carousel_slides_en": ["A developer quoted **480 hours** of work", "Client's budget was just $400 - the internet said that's below minimum wage", "We quote fair, real rates from day one - no lowball surprises later", "What's your project actually worth?"],
  "carousel_slides_ur": ["Developer ne **480 ghante** ka kaam quote kiya", "Client ka budget sirf $400 tha - internet ne kaha ye minimum wage se kam hai", "Hum din 1 se fair rate dete hain - baad mein surprise nahi", "Tumhare project ki keemat kya hai?"],
  "illustration_emotion": "shocked",
  "hashtags": ["#WebDevelopment", "#FreelanceRates", "#TechPricing", "#StartupTools", "#PakistanTech"]
}}

Output format (upar wale example jaisi hi quality, sirf ye JSON, kuch aur text nahi):
[
  {{
    "slot": 1,
    "service": "Web Development",
    "caption_en": "English caption for LinkedIn/X...",
    "caption_ur": "Roman Urdu caption for Facebook...",
    "carousel_slides_en": ["hook with **highlight**", "problem sentence", "solution sentence", "CTA"],
    "carousel_slides_ur": ["hook with **highlight**", "problem sentence", "solution sentence", "CTA"],
    "illustration_emotion": "shocked"
  }},
  ...
]
"""


def _extract_json(text):
    """Model kabhi kabhi ```json fences ya extra text daal deta hai - clean karta hai."""
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"```\s*$", "", text)
    return text.strip()


def generate_with_gemini(topics_summary, num_posts):
    import google.generativeai as genai

    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel(config.GEMINI_MODEL)

    prompt = f"{SYSTEM_PROMPT}\n\nAaj ke trending topics/pain-points:\n{topics_summary}\n\nAb {num_posts} unique posts generate karo."
    response = model.generate_content(prompt)
    return _extract_json(response.text)


def generate_with_claude(topics_summary, num_posts):
    import anthropic

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"Aaj ke trending topics/pain-points:\n{topics_summary}\n\nAb {num_posts} unique posts generate karo."}
        ],
    )
    return _extract_json(message.content[0].text)


def build_topics_summary(topics_data, max_items=15):
    """Manual (Ale ke curated Reddit finds) + Trends topics ko ek readable summary mein convert karta hai."""
    lines = []
    for t in topics_data.get("manual_topics", [])[:max_items]:
        lines.append(f"- [Manually curated] {t}")
    for t in topics_data.get("trends_topics", [])[:max_items]:
        lines.append(f"- [Trending] {t['query']} (related to: {t['seed_keyword']})")
    return "\n".join(lines) if lines else "Koi specific topic nahi mila - general AI automation/agency growth angle se likho."


def generate_daily_posts(num_posts=None):
    if num_posts is None:
        num_posts = config.POSTS_PER_DAY

    topics_path = os.path.join(config.OUTPUT_DIR, "topics.json")
    if os.path.exists(topics_path):
        with open(topics_path, "r", encoding="utf-8") as f:
            topics_data = json.load(f)
    else:
        topics_data = {"manual_topics": [], "trends_topics": []}

    topics_summary = build_topics_summary(topics_data)

    engines = [config.PRIMARY_ENGINE, "claude" if config.PRIMARY_ENGINE == "gemini" else "gemini"]
    raw_output = None
    used_engine = None

    for engine in engines:
        try:
            print(f"Content generate ho raha hai using: {engine}")
            if engine == "gemini":
                raw_output = generate_with_gemini(topics_summary, num_posts)
            else:
                raw_output = generate_with_claude(topics_summary, num_posts)
            used_engine = engine
            break
        except Exception as e:
            print(f"[WARN] {engine} fail ho gaya: {e}. Backup try ho raha hai...")
            continue

    if raw_output is None:
        raise RuntimeError("Dono engines (Gemini + Claude) fail ho gaye. API keys check karo.")

    posts = json.loads(raw_output)

    result = {
        "generated_at": datetime.utcnow().isoformat(),
        "engine_used": used_engine,
        "posts": posts,
    }

    out_path = os.path.join(config.OUTPUT_DIR, "daily_posts.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"{len(posts)} posts generate ho gaye ({used_engine} se). Saved: {out_path}")
    return result


if __name__ == "__main__":
    generate_daily_posts()