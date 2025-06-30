import feedparser
import requests
from bs4 import BeautifulSoup
from parser import extract_and_score
import json
import os

# User input for keywords
print("\n📝 Enter the main keywords:")
main_keywords = input("➤ Main keywords (comma-separated): ").lower().split(",")

print("\n📝 Enter associated keywords (optional):")
assoc_keywords = input("➤ Associated keywords (comma-separated): ").lower().split(",")

# Clean up keywords
KEYWORDS = [kw.strip() for kw in main_keywords + assoc_keywords if kw.strip()]
MAX_RESULTS = 10
MIN_SCORE = 2

results = []

def fetch_article(url):
    try:
        response = requests.get(url, headers={"User-Agent": "NewsRSSBot/1.0"}, timeout=5)
        if response.status_code != 200:
            return False

        soup = BeautifulSoup(response.text, "html.parser")

        # 🔁 Handle canonical redirection
        canonical = soup.find("link", rel="canonical")
        if canonical and canonical.get("href") and canonical["href"] != url:
            url = canonical["href"]
            print(f"🔁 Canonical redirect: {url}")
            response = requests.get(url, headers={"User-Agent": "NewsRSSBot/1.0"}, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")

        text, score, matched = extract_and_score(soup, KEYWORDS)
        if score >= MIN_SCORE:
            print(f"✅ Match ({score}) - {url}")
            print(f"   → Matched Keywords: {matched}")
            results.append({
                "url": url,
                "score": score,
                "matched_keywords": matched,
                "content": text[:1000]
            })
            return True
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
    return False

def load_and_crawl_rss():
    print("\n🚀 Starting RSS news crawler...\n")
    os.makedirs("output", exist_ok=True)

    try:
        with open("rss_feeds.txt") as f:
            feeds = [line.strip() for line in f if line.strip()]

        for feed_url in feeds:
            if len(results) >= MAX_RESULTS:
                break

            print(f"\n🌐 Reading feed: {feed_url}")
            feed = feedparser.parse(feed_url)

            for entry in feed.entries:
                if len(results) >= MAX_RESULTS:
                    break

                article_url = entry.link

                # Skip non-article links (feeds, APIs, WordPress junk)
                if any(ext in article_url for ext in [".xml", ".rss", "feed", "wp-json", "comment", ".php?"]):
                    continue

                fetch_article(article_url)

        if results:
            with open("output/rss_data.json", "w", encoding="utf-8") as out:
                json.dump(results, out, ensure_ascii=False, indent=2)
            print(f"\n✅ {len(results)} relevant articles saved to output/rss_data.json")
        else:
            print("\n⚠️ No relevant articles found.")

    except FileNotFoundError:
        print("❌ rss_feeds.txt not found! Add some RSS feed URLs first.")

if __name__ == "__main__":
    load_and_crawl_rss()
