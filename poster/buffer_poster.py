"""
Buffer Poster - daily_posts.json (captions) + GitHub-hosted carousel images
ko Buffer ke NAYE GraphQL API (api.buffer.com) se queue mein daal deta hai.

ZAROORI 2026 UPDATE: Buffer ne apna purana REST/OAuth developer-apps system
band kar diya hai naye developers ke liye. Ab sirf GraphQL API hai, jisme:
1. Auth ek "Personal API Key" se hota hai (Buffer Settings > API se milta hai,
   purana "create an app" wala tareeqa nahi)
2. Images ka DIRECT UPLOAD nahi hota - Buffer ko ek PUBLIC IMAGE URL chahiye.
   Isliye GitHub Actions workflow pehle generated images ko wapis repo mein
   commit/push karta hai (repo PUBLIC hona chahiye), aur ye script un images
   ka raw.githubusercontent.com URL bana ke Buffer ko deta hai.
"""

import sys
import os
import json
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

BUFFER_API_URL = "https://api.buffer.com"

# GitHub Actions khud ye env variable set karta hai (owner/repo)
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "")
GITHUB_BRANCH = os.environ.get("GITHUB_REF_NAME", "main")


def _local_path_to_public_url(local_path):
    """Local file path (output/images/...) ko raw.githubusercontent.com public URL mein convert karta hai.
    Zaroori: repo PUBLIC hona chahiye, warna Buffer ye URL fetch nahi kar payega."""
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rel_path = os.path.relpath(local_path, repo_root).replace(os.sep, "/")
    return f"https://raw.githubusercontent.com/{GITHUB_REPOSITORY}/{GITHUB_BRANCH}/{rel_path}"


def _graphql_request(query, variables=None):
    response = requests.post(
        BUFFER_API_URL,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.BUFFER_ACCESS_TOKEN}",
        },
        json={"query": query, "variables": variables or {}},
    )
    data = response.json()

    if "errors" in data and data["errors"]:
        raise RuntimeError(f"Buffer GraphQL error: {data['errors'][0].get('message')}")

    return data.get("data", {})


CREATE_POST_MUTATION = """
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    ... on PostActionSuccess {
      post { id text }
    }
    ... on MutationError {
      message
    }
  }
}
"""


def add_to_buffer(channel_id, text, image_paths=None, service=None):
    """Ek post ko ek Buffer channel ki queue mein add karta hai (naya GraphQL tareeqa).
    schedulingType: automatic + mode: addToQueue - matlab Buffer apne set-kiye-hue
    posting-times schedule mein agli khali slot mein daal dega.
    'service' (facebook/twitter/linkedin) ke hisaab se platform-specific metadata add karta hai."""

    assets = []
    if image_paths:
        for img_path in image_paths:
            if os.path.exists(img_path):
                public_url = _local_path_to_public_url(img_path)
                assets.append({"image": {"url": public_url}})

    post_input = {
        "text": text,
        "channelId": channel_id,
        "schedulingType": "automatic",
        "mode": "addToQueue",
        "assets": assets,  # zaroori field hai, khali array bhi chalega (text-only post ke liye)
    }

    # Instagram ko Buffer ka API explicitly batana zaroori hai ye kis type ka post hai
    # (post/story/reel) - warna "Invalid post" error deta hai. Hum hamesha normal feed "post" bhejte hain.
    if service == "instagram":
        post_input["metadata"] = {"instagram": {"type": "post"}}

    variables = {"input": post_input}

    result = _graphql_request(CREATE_POST_MUTATION, variables)
    create_result = result.get("createPost", {})

    if create_result.get("message"):
        raise RuntimeError(f"Buffer post fail: {create_result['message']}")

    return create_result


# Kaunse platform pe kaunsi language jayegi (Facebook hata diya gaya, Instagram add hua)
PLATFORM_LANGUAGE = {
    "linkedin": "en",
    "twitter": "en",
    "instagram": "en",
}


def _fit_to_twitter_limit(text, limit=280):
    """X (Twitter) 280 characters se zyada allow nahi karta - agar caption lambi ho
    to aakhri poore sentence tak chhota kar deta hai (beech mein se nahi katta)."""
    if len(text) <= limit:
        return text

    truncated = text[: limit - 1]
    last_period = truncated.rfind(". ")
    if last_period > limit * 0.4:  # kaafi lamba hissa bacha to sentence-boundary pe katno
        return truncated[: last_period + 1]
    return truncated.rstrip() + "…"


# Har platform pe kitne hashtags chahiye (LinkedIn zyada helpful, X kam space/relevance)
HASHTAG_COUNT = {
    "linkedin": 5,
    "instagram": 4,
    "twitter": 2,
}


def _build_final_caption(caption, hashtags, platform):
    """Caption ke aakhir mein website link + platform ke hisaab se sahi tadaad mein
    hashtags jod deta hai. Twitter ke liye pehle in dono ki jagah reserve karta hai,
    phir caption ko us hisaab se fit karta hai - taake kabhi beech mein se na katein."""
    count = HASHTAG_COUNT.get(platform, 3)
    tags = hashtags[:count] if hashtags else []
    tag_line = " ".join(tags)
    website_line = "🌐 kreafy.online"

    extra_lines = "\n\n".join([line for line in [website_line, tag_line] if line])
    reserved = len(extra_lines) + 2 if extra_lines else 0  # +2 for the blank line before it

    if platform == "twitter":
        caption = _fit_to_twitter_limit(caption, limit=280 - reserved)

    if extra_lines:
        return f"{caption}\n\n{extra_lines}"
    return caption


def post_hottake_content(platforms):
    """Hot-take YA emotional-story - dono single-image formats - isi function se post hote
    hain (dono output/hottake_post.json + output/hottake/manifest.json use karte hain).
    'platforms' schedule.json se aata hai (jaise Sunday ko LinkedIn skip hota hai)."""
    hottake_json = os.path.join(config.OUTPUT_DIR, "hottake_post.json")
    manifest_path = os.path.join(config.OUTPUT_DIR, "hottake", "manifest.json")

    with open(hottake_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    post = data.get("post", {})

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    success_count = 0
    fail_count = 0

    for platform in platforms:
        channel_id = config.BUFFER_PROFILE_IDS.get(platform, "")
        if not channel_id:
            print(f"[SKIP] {platform}: channel ID set nahi hai")
            continue

        # Twitter ko 16:9 wide image chahiye, baaki (LinkedIn/Instagram) ko 4:5 vertical
        image_path = manifest.get("twitter_image") if platform == "twitter" else manifest.get("main_image")
        caption = post.get(f"caption_{platform}", post.get("caption_linkedin", ""))
        hashtags = post.get("hashtags", [])
        caption = _build_final_caption(caption, hashtags, platform)

        try:
            add_to_buffer(channel_id, caption, [image_path] if image_path else [], service=platform)
            print(f"[OK] Hot-take/emotional post -> {platform} queue mein add ho gayi")
            success_count += 1
        except Exception as e:
            print(f"[FAIL] Hot-take/emotional post -> {platform}: {e}")
            fail_count += 1

    print(f"\nDone. Success: {success_count}, Failed: {fail_count}")


def post_all_daily_content():
    posts_path = os.path.join(config.OUTPUT_DIR, "daily_posts.json")
    images_dir = os.path.join(config.OUTPUT_DIR, "images")
    manifest_path = os.path.join(images_dir, "manifest.json")

    with open(posts_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    manifest = {}
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
            manifest = {p["post_index"]: p for p in manifest_data.get("posts", [])}

    posts = data.get("posts", [])
    success_count = 0
    fail_count = 0

    for i, post in enumerate(posts):
        post_manifest = manifest.get(i + 1, {})

        for platform, channel_id in config.BUFFER_PROFILE_IDS.items():
            if not channel_id:
                continue  # is platform ki channel_id set nahi, skip

            lang = PLATFORM_LANGUAGE.get(platform, "en")  # image assets abhi bhi sirf 2 languages (en/ur) mein bante hain
            caption = post.get(f"caption_{platform}", post.get(f"caption_{lang}", post.get("caption", "")))
            hashtags = post.get("hashtags", [])
            caption = _build_final_caption(caption, hashtags, platform)

            # LinkedIn aur Instagram dono multi-image ko sequential/swipeable dikhate hain -
            # poora 4-slide carousel dono ko jata hai. Twitter grid mein crop kar deta hai,
            # isliye sirf pehli (hook) slide ek single image ki tarah bhejte hain.
            slides = post_manifest.get(f"slides_{lang}", [])
            if platform == "twitter":
                image_paths = slides[:1] if slides else []
            else:
                image_paths = slides

            try:
                add_to_buffer(channel_id, caption, image_paths, service=platform)
                print(f"[OK] Post {i + 1} ({lang}, {len(image_paths)} slides) -> {platform} queue mein add ho gayi")
                success_count += 1
            except Exception as e:
                print(f"[FAIL] Post {i + 1} -> {platform}: {e}")
                fail_count += 1

    print(f"\nDone. Success: {success_count}, Failed: {fail_count}")
    print("Yaad rakho: pehli baar chalane ke baad Buffer/LinkedIn pe khud check karo ke")
    print("carousel sahi se saari slides ke sath bani hai ya nahi (README ka test step dekho).")


if __name__ == "__main__":
    schedule_path = os.path.join(config.OUTPUT_DIR, "schedule.json")
    with open(schedule_path, "r", encoding="utf-8") as f:
        schedule = json.load(f)

    if schedule.get("run_carousel"):
        post_all_daily_content()
    elif schedule.get("run_hottake") or schedule.get("run_emotional"):
        post_hottake_content(schedule.get("platforms", []))
    else:
        print("Schedule mein aaj ke liye koi format enabled nahi - kuch post nahi hua.")