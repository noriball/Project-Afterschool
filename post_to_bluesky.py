import os
import glob
import json
import datetime
import urllib.request

JST = datetime.timezone(datetime.timedelta(hours=9))
API = "https://bsky.social/xrpc"
REPO_URL = "https://github.com/noriball/Project-Afterschool/blob/main/archives"

# 投稿文にも必ず残す。リンクを踏まない読者には、これが唯一の手がかりになる。
CREDIT = "#放課後のAI ｜ AIによる創作です"
POST_LIMIT = 300


def api_post(path, body, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(
        f"{API}/{path}", data=json.dumps(body).encode("utf-8"), headers=headers
    )
    with urllib.request.urlopen(req) as res:
        return json.load(res)


def extract_excerpt(markdown, limit):
    """見出しと注記を除いた最初の段落を、記事のつかみとして抜き出す。"""
    for block in markdown.split("\n\n"):
        lines = [
            line.strip()
            for line in block.strip().splitlines()
            if line.strip() and not line.strip().startswith((">", "#", "-", "*"))
        ]
        if not lines:
            continue
        text = " ".join(lines)
        return text if len(text) <= limit else text[: limit - 1] + "…"
    return ""


def build_post_text(markdown, filename):
    url = f"{REPO_URL}/{filename}"
    title = f"『放課後のAI』{filename[:10]} 号"
    # 抜粋以外は長さが決まっているので、残った分だけを抜粋に充てる
    fixed = f"{title}\n\n\n\n全文 → {url}\n\n{CREDIT}"
    excerpt = extract_excerpt(markdown, POST_LIMIT - len(fixed))
    return f"{title}\n\n{excerpt}\n\n全文 → {url}\n\n{CREDIT}", url


def link_facet(text, url):
    """URL をリンクとして認識させる。Bluesky の facet は UTF-8 のバイト位置で指定する。"""
    encoded = text.encode("utf-8")
    start = encoded.find(url.encode("utf-8"))
    if start == -1:
        return []
    return [
        {
            "index": {"byteStart": start, "byteEnd": start + len(url.encode("utf-8"))},
            "features": [{"$type": "app.bsky.richtext.facet#link", "uri": url}],
        }
    ]


def main():
    identifier = os.environ.get("BLUESKY_IDENTIFIER")
    password = os.environ.get("BLUESKY_APP_PASSWORD")
    if not identifier or not password:
        # 未設定でもアーカイブ生成まではジョブを緑にしたいので、ここでは落とさない
        print("BLUESKY_IDENTIFIER / BLUESKY_APP_PASSWORD is not set; skipping post.")
        return

    # 今日分に絞ってから最新を選ぶ。生成が失敗した日に過去号を蒸し返さないため。
    date_str = datetime.datetime.now(JST).strftime("%Y-%m-%d")
    todays = sorted(glob.glob(os.path.join("archives", f"{date_str}_*.md")))
    if not todays:
        print(f"No archive for today ({date_str}); nothing to post.")
        return

    path = todays[-1]
    with open(path, encoding="utf-8") as f:
        markdown = f.read()

    text, url = build_post_text(markdown, os.path.basename(path))

    session = api_post(
        "com.atproto.server.createSession",
        {"identifier": identifier, "password": password},
    )
    api_post(
        "com.atproto.repo.createRecord",
        {
            "repo": session["did"],
            "collection": "app.bsky.feed.post",
            "record": {
                "$type": "app.bsky.feed.post",
                "text": text,
                "facets": link_facet(text, url),
                "createdAt": datetime.datetime.now(datetime.timezone.utc)
                .isoformat()
                .replace("+00:00", "Z"),
            },
        },
        token=session["accessJwt"],
    )
    print(f"Posted to Bluesky ({len(text)} chars):\n{text}")


if __name__ == "__main__":
    main()
