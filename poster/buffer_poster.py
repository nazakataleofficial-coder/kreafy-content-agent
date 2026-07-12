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


def add_to_buffer(channel_id, text, image_paths=None):
    """Ek post ko ek Buffer channel ki queue mein add karta hai (naya GraphQL tareeqa).
    schedulingType: automatic + mode: addToQueue - matlab Buffer apne set-kiye-hue
    posting-times schedule mein agli khali slot mein daal dega."""

    assets = []
    if image_paths:
        for img_path in image_paths:
            if os.path.exists(img_path):
                public_url = _local_path_to_public_url(img_path)
                assets.append({"image": {"url": public_url}})

    variables = {
        "input": {
            "text": text,
            "channelId": channel_id,
            "schedulingType": "automatic",
            "mode": "addToQueue",
            "assets": assets,  # zaroori field hai, khali array bhi chalega (text-only post ke liye)
        }
    }

    result = _graphql_request(CREATE_POST_MUTATION, variables)
    create_result = result.get("createPost", {})

    if create_result.get("message"):
        raise RuntimeError(f"Buffer post fail: {create_result['message']}")

    return create_result


# Kaunse platform pe kaunsi language jayegi
PLATFORM_LANGUAGE = {
    "linkedin": "en",
    "twitter": "en",
    "facebook": "ur",
}


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

            lang = PLATFORM_LANGUAGE.get(platform, "en")
            caption = post.get(f"caption_{lang}", post.get("caption", ""))
            image_paths = post_manifest.get(f"slides_{lang}", [])

            try:
                add_to_buffer(channel_id, caption, image_paths)
                print(f"[OK] Post {i + 1} ({lang}, {len(image_paths)} slides) -> {platform} queue mein add ho gayi")
                success_count += 1
            except Exception as e:
                print(f"[FAIL] Post {i + 1} -> {platform}: {e}")
                fail_count += 1

    print(f"\nDone. Success: {success_count}, Failed: {fail_count}")
    print("Yaad rakho: pehli baar chalane ke baad Buffer/LinkedIn pe khud check karo ke")
    print("carousel sahi se saari slides ke sath bani hai ya nahi (README ka test step dekho).")


if __name__ == "__main__":
    post_all_daily_content()
