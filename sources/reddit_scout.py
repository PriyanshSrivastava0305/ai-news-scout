import json
import urllib.request
from typing import List, Dict, Any

REDDIT_URL = "https://www.reddit.com/r/LocalLLaMA/new.json?limit=25"

class RedditScout:
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AI-News-Scout/1.0"}

    def fetch_recent_drops(self) -> List[Dict[str, Any]]:
        results = []
        try:
            req = urllib.request.Request(REDDIT_URL, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                posts = data.get("data", {}).get("children", [])
                for p in posts:
                    post = p.get("data", {})
                    post_id = post.get("id", "")
                    title = post.get("title", "")
                    selftext = post.get("selftext", "")
                    permalink = post.get("permalink", "")
                    url = post.get("url", f"https://reddit.com{permalink}")
                    flair = (post.get("link_flair_text") or "").lower()
                    author = post.get("author", "")
                    ups = post.get("ups", 0)

                    # Only consider posts that look like announcements, models, or releases
                    relevant_flairs = ["news", "new model", "release", "discussion", "benchmark"]
                    is_flair_match = any(rf in flair for rf in relevant_flairs) or not flair
                    
                    if post_id and title and is_flair_match:
                        results.append({
                            "id": f"reddit:{post_id}",
                            "title": title,
                            "description": selftext[:600] if selftext else title,
                            "url": f"https://www.reddit.com{permalink}",
                            "source": "Reddit r/LocalLLaMA",
                            "author": author,
                            "tags": ["reddit", "localllama", flair],
                            "extra": {
                                "flair": flair,
                                "upvotes": ups
                            }
                        })
        except Exception as e:
            print(f"[Reddit Scout] Notice: {e}")

        return results
