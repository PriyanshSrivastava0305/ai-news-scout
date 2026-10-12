import json
import urllib.request
from typing import List, Dict, Any

HF_MODELS_URL = "https://huggingface.co/api/models?sort=createdAt&direction=-1&limit=40"
HF_TRENDING_URL = "https://huggingface.co/api/models?sort=trendingScore&direction=-1&limit=30"
HF_PAPERS_URL = "https://huggingface.co/api/daily_papers"

class HuggingFaceScout:
    def __init__(self):
        self.headers = {"User-Agent": "AI-News-Scout/1.0"}

    def fetch_recent_models(self) -> List[Dict[str, Any]]:
        results = []
        try:
            req = urllib.request.Request(HF_MODELS_URL, headers=self.headers)
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for m in data:
                    model_id = m.get("id", "")
                    if not model_id:
                        continue
                    tags = m.get("tags", [])
                    pipeline = m.get("pipeline_tag", "")
                    downloads = m.get("downloads", 0)
                    likes = m.get("likes", 0)
                    
                    results.append({
                        "id": f"hf-model:{model_id}",
                        "title": model_id,
                        "description": f"New Hugging Face model release by {model_id.split('/')[0] if '/' in model_id else 'Community'}. Pipeline: {pipeline}. Tags: {', '.join(tags[:8])}",
                        "url": f"https://huggingface.co/{model_id}",
                        "source": "Hugging Face Hub",
                        "author": model_id.split('/')[0] if '/' in model_id else "Community",
                        "tags": tags,
                        "extra": {
                            "pipeline_tag": pipeline,
                            "downloads": downloads,
                            "likes": likes
                        }
                    })
        except Exception as e:
            print(f"[HF Scout] Error fetching models: {e}")

        # Also fetch daily papers (which highlight breakthrough models)
        try:
            req = urllib.request.Request(HF_PAPERS_URL, headers=self.headers)
            with urllib.request.urlopen(req, timeout=12) as resp:
                papers = json.loads(resp.read().decode("utf-8"))
                for p in papers:
                    paper_data = p.get("paper", {})
                    paper_id = paper_data.get("id", "")
                    title = paper_data.get("title", "")
                    summary = paper_data.get("summary", "")
                    if not paper_id or not title:
                        continue
                    
                    results.append({
                        "id": f"hf-paper:{paper_id}",
                        "title": title,
                        "description": summary,
                        "url": f"https://huggingface.co/papers/{paper_id}",
                        "source": "Hugging Face Daily Papers",
                        "author": "ArXiv / HF Papers",
                        "tags": ["paper", "research", "ai"],
                        "extra": {
                            "paper_id": paper_id,
                            "upvotes": p.get("paper", {}).get("upvotes", 0)
                        }
                    })
        except Exception as e:
            print(f"[HF Scout] Error fetching papers: {e}")

        return results
