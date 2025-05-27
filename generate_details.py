import json
import os
import re
import requests
from pathlib import Path

API_URL = "https://api.anthropic.com/v1/messages"
API_KEY = os.getenv("CLAUDE_API_KEY")


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower())
    return slug.strip("-")


def fetch_website_content(url: str) -> str:
    response = requests.get(url, timeout=10)
    return response.text[:5000]


def generate_detail(brand: str, website: str, description: str, content: str) -> str:
    if not API_KEY:
        raise RuntimeError("CLAUDE_API_KEY environment variable not set")

    prompt = (
        f"Write a concise 2-3 paragraph overview for the business {brand}. "
        f"Use the following existing description: {description}. "
        f"Here is some content from the website: {content}."
    )

    payload = {
        "model": "claude-4",
        "max_tokens": 300,
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    resp = requests.post(API_URL, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    # anthropic API returns messages content list
    return data["content"][0]["text"]


def main() -> None:
    with open("affiliates.json") as f:
        affiliates = json.load(f)

    updated = False
    for site in affiliates:
        if site.get("detail"):
            continue
        try:
            content = fetch_website_content(site["website"])
            site["detail"] = generate_detail(site["brand"], site["website"], site["description"], content)
            updated = True
        except Exception as exc:
            print(f"Failed generating detail for {site['brand']}: {exc}")

    if updated:
        Path("affiliates.json").write_text(json.dumps(affiliates, indent=4))
        print("Updated affiliates.json with details")
    else:
        print("No updates were made")


if __name__ == "__main__":
    main()
