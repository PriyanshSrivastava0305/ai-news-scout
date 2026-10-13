import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

SETTINGS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "settings.json")

class NtfyNotifier:
    def __init__(self, settings_path: str = SETTINGS_PATH):
        self.settings = self.load_settings(settings_path)
        
        # Ensure topic falls back to settings.json even if NTFY_TOPIC is passed as empty string
        env_topic = (os.getenv("NTFY_TOPIC") or "").strip()
        self.topic = env_topic or self.settings.get("ntfy_topic") or "ai-news-scout-alert-94b2f1"
        
        env_server = (os.getenv("NTFY_SERVER") or "").strip()
        self.server = (env_server or self.settings.get("ntfy_server") or "https://ntfy.sh").rstrip("/")

    def load_settings(self, path: str) -> Dict[str, Any]:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def send_notification(
        self,
        title: str,
        short_summary: str,
        expanded_details: str,
        url: str,
        priority: str = "default",
        tags: Optional[str] = "robot,rocket"
    ) -> bool:
        """
        Sends an alert to ntfy.sh using JSON payload (full UTF-8 support for emojis & rich markdown).
        - Phone / Laptop system banner: Shows title + 1-2 lines short summary.
        - Tapped / Opened in ntfy app: Shows full expanded breakdown and action buttons.
        """
        if not self.topic:
            print("[Notifier] Error: No ntfy topic specified!")
            return False

        endpoint = f"{self.server}"

        # Combine short summary with expandable section
        full_message = (
            f"{short_summary}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📖 EXPANDED DOSSIER\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{expanded_details}"
        )

        prio_num = 3
        if priority == "high":
            prio_num = 4
        elif priority == "urgent":
            prio_num = 5

        tag_list = [t.strip() for t in (tags or "robot,rocket").split(",") if t.strip()]

        payload = {
            "topic": self.topic,
            "title": title,
            "message": full_message,
            "priority": prio_num,
            "tags": tag_list,
            "click": url,
            "actions": [
                {
                    "action": "view",
                    "label": "🌐 Open Weights / Repo",
                    "url": url
                }
            ]
        }

        try:
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                endpoint,
                data=req_data,
                headers={"Content-Type": "application/json; charset=utf-8"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                return resp.status in (200, 201)
        except urllib.error.HTTPError as e:
            print(f"[Notifier] HTTP Error {e.code}: {e.reason} (topic: '{self.topic}')")
            return False
        except Exception as e:
            print(f"[Notifier] Error sending notification: {e}")
            return False
