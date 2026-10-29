import time
import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


START_URL = "https://www.musashino-u.ac.jp/"


page_dict = {}

# すでにアクセスしたURLを保存
visited = set()


DOMAIN = urlparse(START_URL).netloc


def crawl(url):
    # すでにアクセス済みなら何もしない
    if url in visited:
        return
    visited.add(url)

    print(f"アクセス中: {url}")

    # Webサイトへの負荷を軽減
    time.sleep(1)

    response = requests.get(url)

    # 正常に取得できなかった場合
    if response.status_code != 200:
        print(f"取得失敗: {response.status_code} {url}")
        return

    # Content-Typeを取得
    content_type = response.headers.get("Content-Type", "").lower()

    # HTML以外のコンテンツは除外
    if "text/html" not in content_type:
        print(f"HTML以外のため除外: {url} ({content_type})")
        return

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

        # #以降は同じページなので削除
        next_url = next_url.split("#")[0]

        # URLを解析
        parsed_url = urlparse(next_url)

        # http, https以外は無視
        if parsed_url.scheme not in ["http", "https"]:
            continue

        # 武蔵野大学と同じドメインだけを対象に
        if parsed_url.netloc != DOMAIN:
            continue

        response = requests.get(url)

        # レスポンスヘッダーから Content-Type を取得
        content_type = response.headers.get("Content-Type", "").lower()

        if "text/html" not in content_type:
        
         print(f"HTML以外のため除外: {url} ({content_type})")
        
        return

        # リンク先をさらに巡回
        crawl(next_url)


# トップページからクローリング開始
crawl(START_URL)


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