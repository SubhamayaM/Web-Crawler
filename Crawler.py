import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from parser import extract_and_score
import json
import os

visited = set()
results = []
headers = {"User-Agent": "GenericNewsCrawler/1.0"}

# Prompt for keywords
print("\n📝 Enter the main keywords (e.g., technology, war, climate):")
main_keywords = input("➤ Main keywords (comma-separated): ").lower().split(",")

print("\n📝 Enter associated keywords (optional, e.g., AI, UN, economy):")
assoc_keywords = input("➤ Associated keywords (comma-separated): ").lower().split(",")

# Clean and combine keywords
KEYWORDS = [kw.strip() for kw in main_keywords + assoc_keywords if kw.strip()]

MAX_DEPTH = 2
MAX_RESULTS = 10  # Strict cap on final output count

def crawl(url, depth=0):
    if depth > MAX_DEPTH or url in visited or len(results) >= MAX_RESULTS:
        return
    visited.add(url)

    print(f"🌐 Visiting: {url} (Depth {depth})")

    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200 and "text/html" in response.headers.get("Content-Type", ""):
            soup = BeautifulSoup(response.text, "html.parser")
            text, score = extract_and_score(soup, KEYWORDS)

            if score > 0:
                print(f"✅ Match Score {score:.2f} | {url}")
                results.append({"url": url, "score": score, "content": text[:1000]})

            for link in soup.find_all("a", href=True):
                if len(results) >= MAX_RESULTS:
                    break
                next_url = urljoin(url, link['href'])
                if urlparse(next_url).scheme.startswith("http"):
                    crawl(next_url, depth + 1)
        else:
            print(f"⚠️ Skipped non-HTML or bad response: {url}")
    except Exception as e:
        print(f"❌ Error visiting {url}: {e}")

def load_seed_and_run():
    print("\n🚀 Starting the news crawler...\n")
    os.makedirs("output", exist_ok=True)

    try:
        with open("seed.txt") as f:
            seed_urls = [line.strip() for line in f if line.strip()]
            if not seed_urls:
                print("⚠️ No URLs found in seed.txt.")
                return

            for url in seed_urls:
                if len(results) >= MAX_RESULTS:
                    break
                crawl(url)

        if results:
            # Sort by score descending and limit to top N
            top_results = sorted(results, key=lambda x: x['score'], reverse=True)[:MAX_RESULTS]
            with open("output/crawled_data.json", "w", encoding="utf-8") as out:
                json.dump(top_results, out, ensure_ascii=False, indent=2)
            print(f"\n✅ Done. {len(top_results)} top-matching articles saved to output/crawled_data.json")
        else:
            print("\n⚠️ No matching content found with the given keywords.")

    except FileNotFoundError:
        print("❌ seed.txt not found!")

if __name__ == "__main__":
    load_seed_and_run()
