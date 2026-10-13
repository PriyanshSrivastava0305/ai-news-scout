import os
import re
import json
import urllib.request
from typing import Dict, Any, Tuple

class NewsSummarizer:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

    def format_drop(self, item: Dict[str, Any], match_info: Dict[str, Any]) -> Tuple[str, str, str]:
        """
        Returns:
            title_str: Clean notification title (1 line)
            short_preview: Exactly 1-2 lines shown on phone lockscreen/laptop toast
            expanded_details: Clean mobile Markdown with bullet points:
                              - What makes it special
                              - Where can this be used
                              - Specs & Links
        """
        raw_title = item.get("title", "").strip()
        topic_name = match_info.get("topic_name", "AI")
        clean_title = raw_title.replace("\n", " ").strip()
        if len(clean_title) > 55:
            clean_title = clean_title[:52] + "..."

        title_str = f"🚀 [{topic_name}] {clean_title}"

        # 1. If it's a curated spotlight paper with predefined analysis:
        extra = item.get("extra", {})
        if extra.get("special") and extra.get("use_cases"):
            short_preview = f"{clean_title}: {extra['special'][:140]}..."
            expanded_details = self._format_clean_card(
                item=item,
                topic_name=topic_name,
                special_bullets=[extra["special"]],
                use_case_bullets=[extra["use_cases"]],
                specs=extra.get("specs", "")
            )
            return title_str, short_preview, expanded_details

        # 2. If Gemini API key is available, use LLM for synthesis
        if self.gemini_api_key:
            llm_short, llm_expanded = self._summarize_with_gemini(item, match_info)
            if llm_short and llm_expanded:
                return title_str, llm_short, llm_expanded

        # 3. Smart local heuristic synthesis
        short_preview, expanded_details = self._synthesize_locally(item, match_info)
        return title_str, short_preview, expanded_details

    def _synthesize_locally(self, item: Dict[str, Any], match_info: Dict[str, Any]) -> Tuple[str, str]:
        title = item.get("title", "")
        author = item.get("author", "Community")
        desc = item.get("description", "")
        topic = match_info.get("topic_name", "")
        tags = item.get("tags", [])
        extra = item.get("extra", {})

        # Derive "What Makes It Special" & "Where Can This Be Used"
        special_bullets = []
        use_case_bullets = []

        if "Video" in topic:
            special_bullets.append("Advances high-fidelity video synthesis and temporal consistency.")
            special_bullets.append("Capable of generating dynamic scenes from text or image prompts.")
            use_case_bullets.append("Creative media production, cinematics, and visual content generation.")
            use_case_bullets.append("World model simulation for physics and robotics research.")
        elif "Agent" in topic:
            special_bullets.append("Built for autonomous tool calling, multi-step reasoning, and external API execution.")
            special_bullets.append("Optimized for long-horizon planning and deterministic system workflows.")
            use_case_bullets.append("Autonomous coding assistants, browser automation bots, and DevOps tasks.")
            use_case_bullets.append("Multi-agent collaborative systems and enterprise knowledge retrieval.")
        elif "ASR" in topic or "Speech-to-Text" in topic:
            special_bullets.append("Trained on diverse speech datasets for high-accuracy audio transcription.")
            special_bullets.append("Robust across accents, noisy acoustic environments, and technical terminology.")
            use_case_bullets.append("Real-time live captioning, voice interface assistants, and meeting transcription.")
            use_case_bullets.append("Audio-to-text indexing and multimodal speech-language modeling.")
        elif "TTS" in topic or "Voice" in topic:
            special_bullets.append("Produces natural, expressive voice synthesis with zero-shot voice cloning capabilities.")
            special_bullets.append("Low-latency synthesis suitable for interactive voice agents.")
            use_case_bullets.append("AI podcast narration, character dialogue for gaming, and video voiceovers.")
            use_case_bullets.append("Real-time conversational voice bots and accessibility tools.")
        elif "Architectures" in topic:
            special_bullets.append("Novel architecture exploring alternatives to standard quadratic attention.")
            special_bullets.append("Features enhanced computational efficiency, sub-quadratic scaling, or test-time compute.")
            use_case_bullets.append("Long-context document processing and continuous streaming inference.")
            use_case_bullets.append("Low-latency execution on resource-constrained edge hardware.")
        elif "Company" in topic or "Legal" in topic:
            special_bullets.append(f"Major industry development reported by {author}.")
            special_bullets.append("Highlights regulatory, antitrust, or strategic shifts in top frontier labs.")
            use_case_bullets.append("Tracking legal precedents, AI compliance requirements, and government oversight.")
            use_case_bullets.append("Assessing market impact and enterprise risk management.")
        else: # New LLMs
            special_bullets.append("Open foundation model weights released for the AI developer ecosystem.")
            special_bullets.append("Incorporates recent post-training alignments (DPO, RL, or instruction tuning).")
            use_case_bullets.append("Local self-hosted reasoning, code generation, and domain-specific fine-tuning.")
            use_case_bullets.append("Efficient inference pipelines using GGUF, vLLM, or Ollama.")

        # Clean 1-2 line short preview
        short_preview = f"{title}: {special_bullets[0]}"
        if len(short_preview) > 150:
            short_preview = short_preview[:147] + "..."

        specs_str = f"Source: {item.get('source')} | By: {author}"
        if extra.get("likes") or extra.get("downloads"):
            specs_str += f" | {extra.get('likes', 0)} likes, {extra.get('downloads', 0)} downloads"

        expanded_details = self._format_clean_card(
            item=item,
            topic_name=topic,
            special_bullets=special_bullets,
            use_case_bullets=use_case_bullets,
            specs=specs_str
        )

        return short_preview, expanded_details

    def _format_clean_card(
        self,
        item: Dict[str, Any],
        topic_name: str,
        special_bullets: list,
        use_case_bullets: list,
        specs: str = ""
    ) -> str:
        lines = []
        lines.append(f"*{item.get('title')}*")
        lines.append(f"🏷️ Category: {topic_name}")
        lines.append("")
        lines.append("✨ **What Makes It Special:**")
        for b in special_bullets:
            lines.append(f"• {b}")
        lines.append("")
        lines.append("🎯 **Where Can This Be Used:**")
        for u in use_case_bullets:
            lines.append(f"• {u}")
        lines.append("")
        if specs:
            lines.append(f"⚙️ **Key Specs & Metadata:**\n• {specs}")
            lines.append("")
        lines.append(f"🔗 **Link:** {item.get('url')}")
        return "\n".join(lines)

    def _summarize_with_gemini(self, item: Dict[str, Any], match_info: Dict[str, Any]):
        try:
            title = item.get("title", "")
            desc = item.get("description", "")
            topic = match_info.get("topic_name", "")

            prompt = (
                f"You are an AI research scout. Analyze this release/paper.\n"
                f"Title: {title}\n"
                f"Topic: {topic}\n"
                f"Description: {desc}\n\n"
                f"Output strictly JSON with these keys:\n"
                f"1. 'short_preview': Exactly 1-2 lines summarizing the core achievement (under 140 chars).\n"
                f"2. 'what_makes_it_special': An array of 2 punchy bullet points explaining why it's good or novel.\n"
                f"3. 'where_can_this_be_used': An array of 2 concrete real-world use cases.\n"
                f"4. 'specs': A concise 1-line string of specs/license/parameters."
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
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                res = json.loads(text)

                short_preview = res.get("short_preview", f"{title}: New release in {topic}.")
                expanded = self._format_clean_card(
                    item=item,
                    topic_name=topic,
                    special_bullets=res.get("what_makes_it_special", ["High-impact open source release."]),
                    use_case_bullets=res.get("where_can_this_be_used", ["Developer and enterprise applications."]),
                    specs=res.get("specs", "")
                )
                return short_preview, expanded
        except Exception:
            return None, None
