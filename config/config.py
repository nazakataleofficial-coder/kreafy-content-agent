"""
Kreafy Content Agent - Central Config
Sab API keys yahan se load hoti hain (environment variables se).
"""

import os

# ---------- REDDIT API ----------
REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.environ.get("REDDIT_USER_AGENT", "kreafy-content-agent/1.0")

REDDIT_SUBREDDITS = [
    "webdev", "Entrepreneur", "SaaS", "smallbusiness", "automation",
    "Pakistan", "artificial", "reactnative", "flutterdev", "NewTubers",
    "PartneredYoutube", "faceless_youtube", "animation", "vfx",
]

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

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = "claude-sonnet-4-6"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-3.5-flash"

PRIMARY_ENGINE = os.environ.get("PRIMARY_ENGINE", "gemini")

BUFFER_ACCESS_TOKEN = os.environ.get("BUFFER_ACCESS_TOKEN", "")
# Facebook jaan-bujh kar hata diya gaya hai (high-ticket US/UK/ME audience goal se match
# nahi karta - FB ka strong audience local/low-ticket hota hai). Agar kabhi Instagram
# automation ke liye ek silent FB Page bananі pare (Meta ki backend requirement), wo Page
# kabhi active post nahi karega - is dict mein bhi shamil nahi hai.
BUFFER_PROFILE_IDS = {
    "linkedin": os.environ.get("BUFFER_LINKEDIN_ID", ""),
    "twitter": os.environ.get("BUFFER_TWITTER_ID", ""),
    "instagram": os.environ.get("BUFFER_INSTAGRAM_ID", ""),
}

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

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")

GOOGLE_DOC_ID = os.environ.get("GOOGLE_TOPICS_DOC_ID", "162fofOuGsVnnI9SPMkG9rU82-ph5T4mXSjzuZOpx5-4")
GOOGLE_SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")