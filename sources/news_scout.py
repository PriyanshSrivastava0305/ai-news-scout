import json
import urllib.request
import xml.etree.ElementTree as ET
import hashlib
from typing import List, Dict, Any

GOOGLE_NEWS_AI_LEGAL_URL = (
    "https://news.google.com/rss/search?"
    "q=(OpenAI+OR+Anthropic+OR+Google+OR+Meta+OR+Nvidia+OR+Microsoft)+AND+"
    "(investigation+OR+lawsuit+OR+antitrust+OR+FTC+OR+DOJ+OR+subpoena+OR+government+OR+copyright+OR+ban)+when:3d"
    "&hl=en-US&gl=US&ceid=US:en"
)

HN_TOP_STORIES_URL = (
    "https://hn.algolia.com/api/v1/search_by_date?"
    "tags=story&query=OpenAI+OR+Anthropic+OR+Nvidia+OR+DeepSeek+OR+AI+investigation+OR+FTC+OR+antitrust&hitsPerPage=20"
)

class IndustryNewsScout:
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AI-News-Scout/1.0"}

    def fetch_recent_drops(self) -> List[Dict[str, Any]]:
        results = []
        
        # 1. Google News RSS: AI Company & Government / Investigation Issues
        try:
            req = urllib.request.Request(GOOGLE_NEWS_AI_LEGAL_URL, headers=self.headers)
            with urllib.request.urlopen(req, timeout=12) as resp:
                xml_data = resp.read()
                root = ET.fromstring(xml_data)
                
                for item in root.findall(".//item")[:25]:
                    title_elem = item.find("title")
                    link_elem = item.find("link")
                    pub_date = item.find("pubDate")
                    source_elem = item.find("source")

                    if title_elem is None or link_elem is None:
                        continue

                    title = (title_elem.text or "").strip()
                    url = (link_elem.text or "").strip()
                    source_name = source_elem.text if source_elem is not None else "News"
                    pub = pub_date.text if pub_date is not None else ""

                    # Create stable hash for ID
                    item_hash = hashlib.md5(title.encode("utf-8")).hexdigest()[:12]

                    results.append({
                        "id": f"gnews:{item_hash}",
                        "title": title,
                        "description": f"Breaking legal / regulatory / company news reported by {source_name}. Published: {pub}",
                        "url": url,
                        "source": f"News: {source_name}",
                        "author": source_name,
                        "tags": ["news", "legal", "investigation", "government", "company-news"],
                        "extra": {
                            "publisher": source_name,
                            "published": pub
                        }
                    })
        except Exception as e:
            print(f"[News Scout] Error fetching Google News: {e}")

        # 2. Hacker News: Breaking tech discussions and announcements
        try:
            req = urllib.request.Request(HN_TOP_STORIES_URL, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for hit in data.get("hits", []):
                    object_id = hit.get("objectID")
                    title = hit.get("title") or hit.get("story_title")
                    story_url = hit.get("url") or f"https://news.ycombinator.com/item?id={object_id}"
                    points = hit.get("points", 0)

                    # Only include stories with some traction (e.g., >= 5 points)
                    if object_id and title and points >= 5:
                        results.append({
                            "id": f"hn:{object_id}",
                            "title": title,
                            "description": f"Hacker News discussion ({points} points). URL: {story_url}",
                            "url": story_url,
                            "source": "Hacker News",
                            "author": hit.get("author", "Community"),
                            "tags": ["hackernews", "industry", "discussion"],
                            "extra": {
                                "hn_points": points,
                                "comments": hit.get("num_comments", 0)
                            }
                        })
        except Exception as e:
            print(f"[News Scout] Error fetching Hacker News: {e}")

        return results
