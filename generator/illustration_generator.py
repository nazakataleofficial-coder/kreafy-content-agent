"""
Illustration Generator - har post ki story ke mutabiq ek FIXED character
(Disney/Pixar style, same face/hair/clothes har baar) ki pose/expression
generate karta hai, taake carousel mein ek consistent recognizable
character ban jaye - Gemini ke free image-generation model se.

NOTE: Gemini ke image-gen model ka exact naam Google AI Studio mein
badalta rehta hai. Agar ye script "model not found" error de to
https://aistudio.google.com par jaake current image-gen model ka naam
check kar lena aur neeche GEMINI_IMAGE_MODEL update kar dena.
"""

import sys
import os
import json
import base64

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

GEMINI_IMAGE_MODEL = "gemini-2.5-flash-image"  # verify current name in Google AI Studio


def generate_illustration(prompt, out_path):
    import google.generativeai as genai

    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_IMAGE_MODEL)

    full_prompt = (
        f"{config.CHARACTER_DESIGN}. Scene/pose/emotion for this specific story: {prompt}. "
        f"Background: deep emerald or charcoal, simple and clean, no text in image, "
        f"single character, centered, high quality cinematic 3D render."
    )

    response = model.generate_content(full_prompt)

    for part in response.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data is not None:
            image_bytes = base64.b64decode(part.inline_data.data) if isinstance(part.inline_data.data, str) else part.inline_data.data
            with open(out_path, "wb") as f:
                f.write(image_bytes)
            return True

    return False


SLIDE_NAMES = ["hook", "problem", "solution", "cta"]

# Agar Gemini kisi wajah se fail ho jaye (rate limit, model down, etc.) to carousel
# kabhi khali/broken na bane - ye fixed poses fallback ke tor pe use hote hain.
FALLBACK_POSES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "character_poses"
)
FALLBACK_POSE_BY_SLIDE = {
    "hook": "shocked.png",
    "problem": "thinking.png",
    "solution": "confident.png",
    "cta": "explaining.png",
}


def _use_fallback(slide_name, out_path):
    fallback_path = os.path.join(FALLBACK_POSES_DIR, FALLBACK_POSE_BY_SLIDE.get(slide_name, "confident.png"))
    if os.path.exists(fallback_path):
        with open(fallback_path, "rb") as src, open(out_path, "wb") as dst:
            dst.write(src.read())
        return True
    return False


def generate_all_illustrations():
    """Har post ki har slide (hook/problem/solution/cta) ke liye ALAG illustration banata hai
    (post.illustration_prompts array se, jo content_generator.py ab per-slide scene deta hai).
    Purane single-illustration format (illustration_prompt_en) ko bhi backward-compat ke
    tor pe support karta hai (agar kabhi wahi field mil jaye to sirf hook ke liye use hoga)."""
    posts_path = os.path.join(config.OUTPUT_DIR, "daily_posts.json")
    illustrations_dir = os.path.join(config.OUTPUT_DIR, "illustrations")
    os.makedirs(illustrations_dir, exist_ok=True)

    with open(posts_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    posts = data.get("posts", [])
    total_slides = 0
    success_count = 0
    fallback_count = 0

    for i, post in enumerate(posts):
        prompts = post.get("illustration_prompts")
        if not prompts or len(prompts) < 4:
            legacy = post.get("illustration_prompt_en", "")
            prompts = [legacy, legacy, legacy, legacy] if legacy else ["", "", "", ""]

        for slide_idx, slide_name in enumerate(SLIDE_NAMES):
            prompt = prompts[slide_idx] if slide_idx < len(prompts) else ""
            out_path = os.path.join(illustrations_dir, f"post_{i + 1}_{slide_name}.png")
            total_slides += 1

            if not prompt:
                print(f"[FALLBACK] Post {i + 1} ({slide_name}): koi prompt nahi mila, fixed pose use ho rahi hai")
                if _use_fallback(slide_name, out_path):
                    fallback_count += 1
                continue

            try:
                ok = generate_illustration(prompt, out_path)
                if ok:
                    print(f"[OK] Post {i + 1} ({slide_name}) illustration ban gayi: {out_path}")
                    success_count += 1
                else:
                    print(f"[FAIL->FALLBACK] Post {i + 1} ({slide_name}): model se image nahi mili, fixed pose use ho rahi hai")
                    if _use_fallback(slide_name, out_path):
                        fallback_count += 1
            except Exception as e:
                print(f"[FAIL->FALLBACK] Post {i + 1} ({slide_name}): {e}")
                if _use_fallback(slide_name, out_path):
                    fallback_count += 1

    print(f"\nTotal {total_slides} slide-illustrations chahiye thi -> {success_count} AI-generated, {fallback_count} fallback pose se.")
    print("Agar zyadatar fallback ho rahi hain, GEMINI_IMAGE_MODEL ka naam check karo is file mein.")


if __name__ == "__main__":
    generate_all_illustrations()
