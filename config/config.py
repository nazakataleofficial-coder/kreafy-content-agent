"""
Kreafy Content Agent - Central Config
Sab API keys yahan se load hoti hain (environment variables se).
Kisi bhi file mein hardcoded key NAHI honi chahiye - taake ye system
kal ko kisi aur client/user ke liye bhi reuse ho sake (multi-tenant ready).
"""

import os

# ---------- REDDIT API ----------
REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.environ.get("REDDIT_USER_AGENT", "kreafy-content-agent/1.0")

# Subreddits jahan se Kreafy ki har service ke pain-points milenge
REDDIT_SUBREDDITS = [
    "webdev",              # Web Development
    "Entrepreneur",
    "SaaS",
    "smallbusiness",
    "automation",
    "Pakistan",
    "artificial",
    "reactnative",         # App Development
    "flutterdev",
    "NewTubers",            # YouTube Automation
    "PartneredYoutube",
    "faceless_youtube",
    "animation",            # 2D/3D Animation
    "vfx",
]

# Fixed character design - Disney/Pixar style semi-realistic 3D character
# (LOCKED per Image 3 reference - same character reused har post mein,
# sirf pose/expression/emotion story ke hisaab se badalta hai. Ise mat badlo
# jab tak explicitly redesign na karna ho - brand recognition isi consistency se banti hai.)
CHARACTER_DESIGN = (
    "Disney/Pixar style 3D character, semi-realistic render, young man mid-20s, "
    "short dark curly hair, warm brown eyes, warm brown skin tone, genuine friendly "
    "smile, wearing a simple casual crew-neck shirt in white or neutral tone "
    "(business-appropriate, no bare chest), soft studio lighting, approachable and "
    "confident expression, upper body portrait framing, clean simple dark background, "
    "no text in image"
)
SERVICE_ROTATION = [
    {"slot": 1, "service": "Web Development", "angle": "Speed/cost comparison vs traditional agencies, case-study proof (Ibn A Hakim jaisa)"},
    {"slot": 2, "service": "App Development", "angle": "Case-study (JaghaDhundo jaisa), broker/middleman commission bachao positioning"},
    {"slot": 3, "service": "YouTube/TikTok Automation", "angle": "Passive income system reveal, faceless channel automation pipeline"},
    {"slot": 4, "service": "2D/3D Animation", "angle": "Before/after visual showcase, unique high-ticket skill, video editing implicitly included"},
    {"slot": 5, "service": "AI Automation / High-ticket proof", "angle": "Alternate daily: AI automation offer OR direct high-ticket case-study/social-proof post"},
]

# ---------- AI CONTENT GENERATION ----------
# Primary
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = "claude-sonnet-4-6"

# Free backup (agar Anthropic credits/subscription na ho)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
# Zaroori: gemini-2.5-pro April 2026 se free tier mein NAHI hai (paid-only ho gaya).
# Flash model free tier mein generous hai (1500 requests/day) - isliye yehi use karo.
GEMINI_MODEL = "gemini-2.5-flash"

# Kaunsa engine pehle try ho - "claude" ya "gemini"
PRIMARY_ENGINE = os.environ.get("PRIMARY_ENGINE", "gemini")  # gemini free hai, default rakha

# ---------- BUFFER (Scheduling/Posting - naya GraphQL API, 2026) ----------
# BUFFER_ACCESS_TOKEN ab asal mein "Personal API Key" hai (Buffer Settings > API se milta hai)
BUFFER_ACCESS_TOKEN = os.environ.get("BUFFER_ACCESS_TOKEN", "")
# Buffer profile IDs ab "Channel IDs" hain (GraphQL API terminology) - har channel
# (LinkedIn/FB/X) ka apna ID hota hai
BUFFER_PROFILE_IDS = {
    "linkedin": os.environ.get("BUFFER_LINKEDIN_ID", ""),
    "facebook": os.environ.get("BUFFER_FACEBOOK_ID", ""),
    "twitter": os.environ.get("BUFFER_TWITTER_ID", ""),
}

# ---------- CONTENT SETTINGS ----------
POSTS_PER_DAY = int(os.environ.get("POSTS_PER_DAY", "5"))
BRAND_NAME = os.environ.get("BRAND_NAME", "Kreafy Digital")
BRAND_NICHE = os.environ.get(
    "BRAND_NICHE",
    "AI automation, web/app development, no-code SaaS building for businesses"
)
BRAND_VOICE = os.environ.get(
    "BRAND_VOICE",
    "Confident, punchy, result-focused. Cinematic hooks. No corporate jargon. "
    "Positions Kreafy Digital as an AI-first agency that builds fast, cheap, and modern "
    "compared to traditional expensive agencies."
)

# ---------- PATHS ----------
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")

# ---------- WEEKLY TOPICS GOOGLE DOC ----------
# "Kreafy Content Agent" Drive folder > "Weekly Topics" doc - Ale yahan hafte mein
# apni Reddit-curated stories paste karta hai. Local manual_topics.txt bhi
# backup ke taur pe kaam karta rehta hai agar Doc access fail ho jaye.
GOOGLE_DOC_ID = os.environ.get("GOOGLE_TOPICS_DOC_ID", "162fofOuGsVnnI9SPMkG9rU82-ph5T4mXSjzuZOpx5-4")
GOOGLE_SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")