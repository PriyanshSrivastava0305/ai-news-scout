import json
import re
import urllib.request
from typing import List, Dict, Any

HF_TRENDING_URL = "https://huggingface.co/api/models?sort=trendingScore&direction=-1&limit=40"
HF_PAPERS_URL = "https://huggingface.co/api/daily_papers"

# Whitelisted top labs & prominent model creators whose drops are always notable
TOP_LABS = {
    "meta-llama", "deepseek-ai", "qwen", "mistralai", "google", "microsoft", 
    "nvidia", "nousresearch", "allenai", "internlm", "thudm", "stabilityai", 
    "black-forest-labs", "openai", "anthropic", "cohere", "tiiuae", 
    "ibm-granite", "bigcode", "vllm-project", "ollama", "bartowski", "comfy-org"
}

# Patterns indicating low-quality, personal experiments or coursework
JUNK_PATTERNS = re.compile(
    r'\b(test|dummy|temp|wip|checkpoint|epoch|step-\d+|cs\d+|rebuttal|homework|draft|lora-v\d+|myawesome)\b',
    re.IGNORECASE
)

class HuggingFaceScout:
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AI-News-Scout/1.0"}

    def fetch_recent_models(self) -> List[Dict[str, Any]]:
        results = []
        
        # 1. Fetch Trending Models (Filtered for real community traction)
        try:
            req = urllib.request.Request(HF_TRENDING_URL, headers=self.headers)
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for m in data:
                    model_id = m.get("id", "")
                    if not model_id:
                        continue
                    
                    author = model_id.split('/')[0].lower() if '/' in model_id else "community"
                    model_name = model_id.split('/')[-1] if '/' in model_id else model_id
                    
                    # Filter out junk/homework/checkpoints
                    if JUNK_PATTERNS.search(model_id):
                        continue

                    likes = m.get("likes", 0)
                    downloads = m.get("downloads", 0)
                    trending_score = m.get("trendingScore", 0)
                    is_top_lab = author in TOP_LABS

                    # Quality gate: Must be from a top lab OR have real community traction
                    if not is_top_lab and likes < 5 and downloads < 50 and trending_score < 3:
                        continue

                    tags = m.get("tags", [])
                    pipeline = m.get("pipeline_tag", "")

                    results.append({
                        "id": f"hf-model:{model_id}",
                        "title": model_id,
                        "description": f"Trending model release by {model_id.split('/')[0]}. Pipeline: {pipeline}. Likes: {likes}, Downloads: {downloads}",
                        "url": f"https://huggingface.co/{model_id}",
                        "source": "Hugging Face Trending",
                        "author": model_id.split('/')[0] if '/' in model_id else "Community",
                        "tags": tags,
                        "extra": {
                            "pipeline_tag": pipeline,
                            "likes": likes,
                            "downloads": downloads,
                            "is_top_lab": is_top_lab
                        }
                    })
        except Exception as e:
            print(f"[HF Scout] Error fetching trending models: {e}")

        # 2. Daily Papers: Hand-curated research papers with community upvotes
        try:
            req = urllib.request.Request(HF_PAPERS_URL, headers=self.headers)
            with urllib.request.urlopen(req, timeout=12) as resp:
                papers = json.loads(resp.read().decode("utf-8"))
                for p in papers:
                    paper_data = p.get("paper", {})
                    paper_id = paper_data.get("id", "")
                    title = paper_data.get("title", "")
                    summary = paper_data.get("summary", "")
                    upvotes = paper_data.get("upvotes", 0)
                    
                    if not paper_id or not title:
                        continue

                    # Only highlight papers that received attention
                    if upvotes < 2:
                        continue

                    results.append({
                        "id": f"hf-paper:{paper_id}",
                        "title": title,
                        "description": summary,
                        "url": f"https://huggingface.co/papers/{paper_id}",
                        "source": "Hugging Face Daily Papers",
                        "author": "Research Preprint",
                        "tags": ["paper", "research", "ai", "curated"],
                        "extra": {
                            "paper_id": paper_id,
                            "upvotes": upvotes
                        }
                    })
        except Exception as e:
            print(f"[HF Scout] Error fetching papers: {e}")

        return results
