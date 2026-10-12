import json
import urllib.request
from typing import List, Dict, Any

GITHUB_SEARCH_URL = "https://api.github.com/search/repositories?q=topic:llm+created:>2024-01-01&sort=updated&order=desc&per_page=25"

KEY_AI_REPOS = [
    "vllm-project/vllm",
    "ollama/ollama",
    "ggerganov/llama.cpp",
    "meta-llama/llama3",
    "QwenLM/Qwen2.5",
    "deepseek-ai/DeepSeek-V3",
    "deepseek-ai/DeepSeek-R1",
    "mistralai/mistral-src",
    "huggingface/transformers",
    "microsoft/autogen"
]

class GitHubScout:
    def __init__(self):
        self.headers = {
            "User-Agent": "AI-News-Scout/1.0",
            "Accept": "application/vnd.github.v3+json"
        }

    def fetch_recent_drops(self) -> List[Dict[str, Any]]:
        results = []
        # Check latest releases for top key repositories
        for repo in KEY_AI_REPOS:
            url = f"https://api.github.com/repos/{repo}/releases/latest"
            try:
                req = urllib.request.Request(url, headers=self.headers)
                with urllib.request.urlopen(req, timeout=6) as resp:
                    rel = json.loads(resp.read().decode("utf-8"))
                    tag_name = rel.get("tag_name", "")
                    rel_name = rel.get("name") or tag_name
                    body = rel.get("body", "")
                    rel_url = rel.get("html_url", "")
                    
                    if tag_name:
                        results.append({
                            "id": f"gh-rel:{repo}:{tag_name}",
                            "title": f"{repo} {rel_name}",
                            "description": body[:500] if body else f"New official release {tag_name} for {repo}",
                            "url": rel_url,
                            "source": "GitHub Releases",
                            "author": repo.split("/")[0],
                            "tags": ["github", "release", repo.split("/")[1]],
                            "extra": {
                                "repository": repo,
                                "tag": tag_name
                            }
                        })
            except Exception:
                # Some repos might not have formal releases, ignore gracefully
                pass

        return results
