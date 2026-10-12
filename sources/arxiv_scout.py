import urllib.request
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

ARXIV_API_URL = "https://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:cs.CL+OR+cat:cs.LG&sortBy=submittedDate&sortOrder=descending&max_results=20"

class ArxivScout:
    def __init__(self):
        self.headers = {"User-Agent": "AI-News-Scout/1.0"}

    def fetch_recent_drops(self) -> List[Dict[str, Any]]:
        results = []
        try:
            req = urllib.request.Request(ARXIV_API_URL, headers=self.headers)
            with urllib.request.urlopen(req, timeout=12) as resp:
                xml_data = resp.read()
                root = ET.fromstring(xml_data)
                
                # Atom namespace
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                
                for entry in root.findall("atom:entry", ns):
                    id_elem = entry.find("atom:id", ns)
                    title_elem = entry.find("atom:title", ns)
                    summary_elem = entry.find("atom:summary", ns)
                    published_elem = entry.find("atom:published", ns)
                    
                    if id_elem is None or title_elem is None:
                        continue
                        
                    raw_id = id_elem.text.strip()
                    arxiv_id = raw_id.split("/abs/")[-1]
                    title = " ".join((title_elem.text or "").split())
                    summary = " ".join((summary_elem.text or "").split())
                    
                    results.append({
                        "id": f"arxiv:{arxiv_id}",
                        "title": title,
                        "description": summary[:600],
                        "url": f"https://arxiv.org/abs/{arxiv_id}",
                        "source": "arXiv AI",
                        "author": "Research Preprint",
                        "tags": ["arxiv", "paper", "research"],
                        "extra": {
                            "arxiv_id": arxiv_id,
                            "published": published_elem.text if published_elem is not None else ""
                        }
                    })
        except Exception as e:
            print(f"[Arxiv Scout] Error: {e}")

        return results
