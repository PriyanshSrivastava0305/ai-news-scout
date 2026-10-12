import os
import json
import urllib.request
from typing import Dict, Any, Tuple

class NewsSummarizer:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

    def format_drop(self, item: Dict[str, Any], match_info: Dict[str, Any]) -> Tuple[str, str, str]:
        """
        Returns:
            title: Short notification title (e.g. '🚀 Qwen-2.5-Coder Released')
            short_summary: Exact 1-2 lines for instant glance on phone lockscreen/laptop banner
            expanded_details: Complete detailed breakdown with links and specs
        """
        source = item.get("source", "Web")
        raw_title = item.get("title", "").strip()
        url = item.get("url", "")
        description = item.get("description", "").strip()
        author = item.get("author", "")
        extra = item.get("extra", {})

        # Clean title
        clean_title = raw_title.replace("\n", " ").strip()
        if len(clean_title) > 60:
            clean_title = clean_title[:57] + "..."

        title_str = f"🚀 [{match_info['topic_name']}] {clean_title}"

        # If Gemini API key is available, use LLM for synthesis
        if self.gemini_api_key:
            llm_short, llm_expanded = self._summarize_with_gemini(raw_title, description, match_info)
            if llm_short:
                return title_str, llm_short, llm_expanded

        # Fallback: Rule-based extraction (clean, reliable, 0 cost)
        short_summary = self._create_rule_based_short_summary(raw_title, description, extra)
        expanded_details = self._create_rule_based_expanded(item, match_info, short_summary)

        return title_str, short_summary, expanded_details

    def _create_rule_based_short_summary(self, title: str, description: str, extra: Dict[str, Any]) -> str:
        # Extract first 1-2 sentences
        desc_clean = " ".join(description.split())
        sentences = [s.strip() for s in desc_clean.split(".") if len(s.strip()) > 10]
        
        if sentences:
            first_sentence = sentences[0] + "."
            # Add second sentence if available and short
            if len(sentences) > 1 and len(first_sentence) < 80:
                short = f"{first_sentence} {sentences[1]}."
            else:
                short = first_sentence
        else:
            short = f"New open-source AI release: {title}."

        # Keep under 160 characters (strict 1-2 lines)
        if len(short) > 160:
            short = short[:157] + "..."
        return short

    def _create_rule_based_expanded(self, item: Dict[str, Any], match_info: Dict[str, Any], short_summary: str) -> str:
        lines = []
        lines.append(f"📌 **Model/Tech:** {item.get('title')}")
        lines.append(f"🏷️ **Topic:** {match_info.get('topic_name')} (Tags: {', '.join(match_info.get('matched_keywords', []))})")
        lines.append(f"🌐 **Source:** {item.get('source')} | By: {item.get('author', 'Community')}")
        lines.append("")
        lines.append("📝 **Summary:**")
        lines.append(f"{short_summary}")
        lines.append("")
        
        extra = item.get("extra", {})
        if extra:
            lines.append("⚙️ **Specs & Highlights:**")
            for k, v in extra.items():
                if v:
                    lines.append(f"• **{k.replace('_', ' ').capitalize()}:** {v}")
            lines.append("")

        lines.append(f"🔗 **Direct Link:** {item.get('url')}")
        return "\n".join(lines)

    def _summarize_with_gemini(self, title: str, description: str, match_info: Dict[str, Any]):
        try:
            prompt = (
                f"You are an AI scout. Summarize this AI release/model drop.\n"
                f"Title: {title}\n"
                f"Description: {description}\n"
                f"Topic: {match_info['topic_name']}\n\n"
                f"Output strictly in JSON with two keys:\n"
                f"1. 'short': Exactly 1 or 2 punchy lines explaining what this model is and why it matters (under 150 chars).\n"
                f"2. 'expanded': A markdown section listing key capabilities, specs, and why it is notable."
            )
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
            req_data = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"response_mime_type": "application/json"}
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(req_data).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                res = json.loads(text)
                return res.get("short"), res.get("expanded")
        except Exception as e:
            # Silently fall back to rule-based summary
            return None, None
