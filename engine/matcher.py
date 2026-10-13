import json
import os
import re
from typing import List, Dict, Any, Optional

TOPICS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "topics.json")
MINIMUM_RELEVANCE_SCORE = 3  # Requires keyword in title (+3) or multiple strong keyword matches

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
        Evaluates whether a drop strongly matches any configured topic.
        Requires high relevance (score >= 3: keyword in title or multiple strong matches).
        """
        combined_text = f"{title} {description} {' '.join(tags or [])}".lower()
        title_lower = title.lower()
        
        best_match = None
        highest_score = 0

        for topic in self.topics:
            matched_keywords = []
            score = 0
            
            for kw in topic.get("keywords", []):
                kw_lower = kw.lower().strip()
                if not kw_lower:
                    continue
                
                pattern = r'\b' + re.escape(kw_lower) + r'\b'
                # Strongest signal: Keyword in Title
                if re.search(pattern, title_lower) or kw_lower in title_lower:
                    matched_keywords.append(kw)
                    score += 3
                elif re.search(pattern, combined_text):
                    matched_keywords.append(kw)
                    score += 1

            if matched_keywords and score >= MINIMUM_RELEVANCE_SCORE and score > highest_score:
                highest_score = score
                best_match = {
                    "topic_id": topic.get("id"),
                    "topic_name": topic.get("name"),
                    "priority": topic.get("priority", "default"),
                    "matched_keywords": matched_keywords,
                    "relevance_score": score
                }

        return best_match
