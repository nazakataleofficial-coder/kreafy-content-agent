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


def generate_all_illustrations():
    posts_path = os.path.join(config.OUTPUT_DIR, "daily_posts.json")
    illustrations_dir = os.path.join(config.OUTPUT_DIR, "illustrations")
    os.makedirs(illustrations_dir, exist_ok=True)

    with open(posts_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    posts = data.get("posts", [])
    success_count = 0

    for i, post in enumerate(posts):
        prompt = post.get("illustration_prompt_en", "")
        if not prompt:
            print(f"[SKIP] Post {i + 1}: koi illustration_prompt_en nahi mila")
            continue

        out_path = os.path.join(illustrations_dir, f"post_{i + 1}.png")
        try:
            ok = generate_illustration(prompt, out_path)
            if ok:
                print(f"[OK] Post {i + 1} illustration ban gayi: {out_path}")
                success_count += 1
            else:
                print(f"[FAIL] Post {i + 1}: model se image nahi mili")
        except Exception as e:
            print(f"[FAIL] Post {i + 1}: {e}")

    print(f"\nTotal {success_count}/{len(posts)} illustrations ban gayeen.")
    print("Agar sab fail huye ho, GEMINI_IMAGE_MODEL ka naam check karo is file mein.")


if __name__ == "__main__":
    generate_all_illustrations()
