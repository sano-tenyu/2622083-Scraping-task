import time
import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
from collections import deque


START_URL = "https://www.musashino-u.ac.jp/"

page_dict = {}

visited = set()

DOMAIN = urlparse(START_URL).netloc

# これからアクセスするURLを保存するキュー
queue = deque([START_URL])

# すでにqueueに追加したURL
queued = {START_URL}


def normalize_url(url):

    parsed = urlparse(url)

    # http:// を https:// に統一
    scheme = "https" if parsed.scheme in ["http", "https"] else parsed.scheme

    # #以降を削除するためfragmentを空文字にする
    normalized = parsed._replace(
        scheme=scheme,
        fragment=""
    )

    return urlunparse(normalized)


while queue:
    # キューの先頭からURLを1つ取り出す
    url = queue.popleft()

    # queueから取り出したのでqueuedから削除
    queued.discard(url)

    # すでにアクセス済みなら無視
    if url in visited:
        continue

    # アクセス済みに追加
    visited.add(url)

    print(f"アクセス中: {url}")

    # Webサイトへの負荷を軽減
    time.sleep(1)

    # Webページを取得
    response = requests.get(url)

    # 正常に取得できなかった場合
    if response.status_code != 200:
        print(f"取得失敗: {response.status_code} {url}")
        continue

    # Content-Typeを取得
    content_type = response.headers.get("Content-Type", "").lower()

    # HTML以外のコンテンツは除外
    if "text/html" not in content_type:
        print(f"HTML以外のため除外: {url} ({content_type})")
        continue

    # HTMLをBeautifulSoupオブジェクトに変換
    soup = BeautifulSoup(response.content, "html.parser")

    # titleを取得
    if soup.title is not None:
        title = soup.title.get_text(strip=True)
    else:
        title = ""

    # 辞書にURLとtitleを保存
    page_dict[url] = title

    # ページ内のaタグをすべて取得
    a_list = soup.find_all("a")

    for a in a_list:
        # href属性を取得
        href = a.get("href")

        # hrefが存在しない場合は無視
        if href is None:
            continue

        # 相対URLを絶対URLに変換
        next_url = urljoin(url, href)

        # URLを正規化
        next_url = normalize_url(next_url)

        # URLを解析
        parsed_url = urlparse(next_url)

        # http, https以外は無視
        if parsed_url.scheme not in ["http", "https"]:
            continue

        # 武蔵野大学と同じドメインだけを対象にする
        if parsed_url.netloc != DOMAIN:
            continue

        # 未アクセスかつqueueにも入っていないURLだけ追加
        if next_url not in visited and next_url not in queued:
            queue.append(next_url)
            queued.add(next_url)


# CSVファイルとして保存
with open(
    "sitemap.csv",
    "w",
    newline="",
    encoding="utf-8-sig"
) as f:

    writer = csv.writer(f)

    # ヘッダー
    writer.writerow(["URL", "title"])

    # 辞書の内容を書き込む
    for url, title in page_dict.items():
        writer.writerow([url, title])


print("取得完了")
print(f"取得ページ数: {len(page_dict)}")