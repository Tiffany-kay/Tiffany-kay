import requests
import re

URL = "https://gql.hashnode.com"
PUBLICATION_HOST = "tiff-explores.hashnode.dev"
POST_COUNT = 3

QUERY = f"""
{{
  publication(host: "{PUBLICATION_HOST}") {{
    posts(first: {POST_COUNT}) {{
      edges {{
        node {{
          title
          url
          publishedAt
        }}
      }}
    }}
  }}
}}
"""

START_MARKER = "<!-- BLOG-POST-LIST:START -->"
END_MARKER = "<!-- BLOG-POST-LIST:END -->"

def fetch_posts():
    response = requests.post(URL, json={"query": QUERY}, timeout=30)
    response.raise_for_status()
    data = response.json()

    edges = (
        data.get("data", {})
        .get("publication", {})
        .get("posts", {})
        .get("edges", [])
    )

    posts = []
    for e in edges:
        node = e.get("node") or {}
        title = node.get("title")
        url = node.get("url")
        date = (node.get("publishedAt") or "")[:10]
        if title and url:
            posts.append(f"* [{title}]({url}) - {date}" if date else f"* [{title}]({url})")
    return posts

def update_readme(new_posts):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    if START_MARKER not in content or END_MARKER not in content:
        raise SystemExit(
            "README.md is missing markers. Add:\n"
            "<!-- BLOG-POST-LIST:START -->\n"
            "<!-- BLOG-POST-LIST:END -->"
        )

    pattern = re.compile(
        rf"({re.escape(START_MARKER)})([\s\S]*?)({re.escape(END_MARKER)})",
        re.MULTILINE,
    )

    replacement = f"{START_MARKER}\n" + "\n".join(new_posts) + f"\n{END_MARKER}"
    new_content, count = pattern.subn(replacement, content)

    if count != 1:
        raise SystemExit(f"Expected to update exactly 1 section, but updated {count}.")

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)

if __name__ == "__main__":
    posts = fetch_posts()
    if posts:
        update_readme(posts)
        print("README updated with latest posts.")
    else:
        print("No posts fetched; README not modified.")
