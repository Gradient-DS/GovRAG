import requests
from bs4 import BeautifulSoup
import json
import os
import time
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse

MAX_ARTICLES = 200
DATA_DIR = "/app/data"
os.makedirs(DATA_DIR, exist_ok=True)

SITES = {
    "nos": {
        "base_url": "https://nos.nl",
        "listing": "/nieuws",
        "output": "scraped_nos.json",
        "link_sel": 'a[href*="/artikel/"]',
        "content_sel": [
            'article',
            'div[class*="article--full__body"]',
            'div[class*="article-content"]'
        ]
    }
}

def fetch_soup(base, path):
    resp = requests.get(base + path, timeout=10)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def find_nos_links(soup, cfg):
    hrefs = [urljoin(cfg["base_url"], a["href"]) 
             for a in soup.select(cfg["link_sel"]) if a.get("href")]
    return list(dict.fromkeys(hrefs))[:MAX_ARTICLES]

def find_nu_links_via_rss(cfg):
    resp = requests.get(cfg["rss_url"], timeout=10)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    links = []
    for item in root.findall(".//item"):
        link = item.findtext("link")
        if link:
            links.append(link.strip())
        if len(links) >= MAX_ARTICLES:
            break
    return links

def scrape_article(url, key, cfg):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        title_el = soup.find("h1")
        title = title_el.get_text(strip=True) if title_el else url

        content_text = None
        if key == "nu":
            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    data = json.loads(script.string)
                except Exception:
                    continue
                items = data if isinstance(data, list) else [data]
                for obj in items:
                    if obj.get("@type") == "NewsArticle" and obj.get("articleBody"):
                        content_text = obj["articleBody"].strip()
                        break
                if content_text:
                    break

        if not content_text:
            body = None
            for sel in cfg["content_sel"]:
                body = soup.select_one(sel)
                if body:
                    break
            if not body:
                body = soup.find("main") or soup.body
            paras = [
                p.get_text(strip=True)
                for p in body.select("p")
                if len(p.get_text(strip=True)) > 50
            ]
            content_text = "\n\n".join(paras)

        if not content_text:
            content_text = "Content not found."

        return {
            "title": title,
            "url": url,
            "source": key,
            "content": content_text
        }

    except Exception as e:
        print(f"[{key}] error scraping {url}: {e}")
        return None

def run_site(key, cfg):
    print(f"\n--- {key.upper()} ---")
    if key == "nos":
        soup = fetch_soup(cfg["base_url"], cfg["listing"])
        links = find_nos_links(soup, cfg)
    else:
        links = find_nu_links_via_rss(cfg)

    print(f"Found {len(links)} links for {key}, limiting to {MAX_ARTICLES}")
    scraped = []
    for url in links[:MAX_ARTICLES]:
        print(f"[{key}] scraping {url}")
        art = scrape_article(url, key, cfg)
        if art and art["content"] != "Content not found.":
            scraped.append(art)
        time.sleep(0.3)

    out_path = os.path.join(DATA_DIR, cfg["output"])
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(scraped, f, ensure_ascii=False, indent=2)

    print(f"[{key}] → {len(scraped)} articles saved to {out_path}")

if __name__ == "__main__":
    for site_key, site_cfg in SITES.items():
        run_site(site_key, site_cfg)
    print("\nAll done.")
