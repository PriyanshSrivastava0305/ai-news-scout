import json
import os
import re
from typing import List, Dict, Any, Optional

TOPICS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "topics.json")

class TopicMatcher:
    def __init__(self, topics_path: str = TOPICS_PATH):
        self.topics_path = topics_path
        self.topics = self.load_topics()

    def load_topics(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.topics_path):
            return []
        try:
            with open(self.topics_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("topics", [])
        except Exception as e:
            print(f"[Matcher] Error loading topics: {e}")
            return []

    def match(self, title: str, description: str, tags: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        Evaluates whether a drop matches any configured topic.
        Returns a dict with matched topic information and score if matched, else None.
        """
        combined_text = f"{title} {description} {' '.join(tags or [])}".lower()
        
        best_match = None
        highest_score = 0

        for topic in self.topics:
            matched_keywords = []
            score = 0
            
            for kw in topic.get("keywords", []):
                kw_lower = kw.lower().strip()
                if not kw_lower:
                    continue
                
                # Check for word boundary or direct occurrence
                pattern = r'\b' + re.escape(kw_lower) + r'\b'
                if re.search(pattern, combined_text):
                    matched_keywords.append(kw)
                    # Higher weight if keyword appears in title
                    if re.search(pattern, title.lower()):
                        score += 3
                    else:
                        score += 1
                elif kw_lower in combined_text:
                    # Partial match for compound terms
                    matched_keywords.append(kw)
                    score += 1

            if matched_keywords and score > highest_score:
                highest_score = score
                best_match = {
                    "topic_id": topic.get("id"),
                    "topic_name": topic.get("name"),
                    "priority": topic.get("priority", "default"),
                    "matched_keywords": matched_keywords,
                    "relevance_score": score
                }

        return best_match
