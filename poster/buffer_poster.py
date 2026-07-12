"""
Buffer Poster - daily_posts.json (captions) + GitHub-hosted carousel images
ko Buffer ke NAYE GraphQL API (api.buffer.com) se queue mein daal deta hai.
"""

import sys
import os
import json
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

BUFFER_API_URL = "https://api.buffer.com"

GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "")
GITHUB_BRANCH = os.environ.get("GITHUB_REF_NAME", "main")


def _local_path_to_public_url(local_path):
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
        "assets": assets,
    }

    if service == "facebook":
        post_input["metadata"] = {"facebook": {"type": "post"}}

    variables = {"input": post_input}

    result = _graphql_request(CREATE_POST_MUTATION, variables)
    create_result = result.get("createPost", {})

    if create_result.get("message"):
        raise RuntimeError(f"Buffer post fail: {create_result['message']}")

    return create_result


PLATFORM_LANGUAGE = {
    "linkedin": "en",
    "twitter": "en",
    "facebook": "ur",
}


def _fit_to_twitter_limit(text, limit=280):
    if len(text) <= limit:
        return text

    truncated = text[: limit - 1]
    last_period = truncated.rfind(". ")
    if last_period > limit * 0.4:
        return truncated[: last_period + 1]
    return truncated.rstrip() + "…"


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
                continue

            lang = PLATFORM_LANGUAGE.get(platform, "en")
            caption = post.get(f"caption_{lang}", post.get("caption", ""))
            if platform == "twitter":
                caption = _fit_to_twitter_limit(caption)
            image_paths = post_manifest.get(f"slides_{lang}", [])

            try:
                add_to_buffer(channel_id, caption, image_paths, service=platform)
                print(f"[OK] Post {i + 1} ({lang}, {len(image_paths)} slides) -> {platform} queue mein add ho gayi")
                success_count += 1
            except Exception as e:
                print(f"[FAIL] Post {i + 1} -> {platform}: {e}")
                fail_count += 1

    print(f"\nDone. Success: {success_count}, Failed: {fail_count}")


if __name__ == "__main__":
    post_all_daily_content()