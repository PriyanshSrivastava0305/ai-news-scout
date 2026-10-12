import os
import sys
import json
import argparse
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from engine.cache import CacheManager
from engine.matcher import TopicMatcher
from engine.summarizer import NewsSummarizer
from engine.notifier import NtfyNotifier

from sources.huggingface import HuggingFaceScout
from sources.github_scout import GitHubScout
from sources.reddit_scout import RedditScout
from sources.arxiv_scout import ArxivScout

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")
TOPICS_PATH = os.path.join(CONFIG_DIR, "topics.json")
SETTINGS_PATH = os.path.join(CONFIG_DIR, "settings.json")


def load_settings():
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_settings(settings):
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def run_scout_cycle(dry_run=False):
    print("=" * 60)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting AI News Scout Cycle...")
    print("=" * 60)

    settings = load_settings()
    cache = CacheManager()
    matcher = TopicMatcher()
    summarizer = NewsSummarizer()
    notifier = NtfyNotifier()

    print(f"• Active topics tracked: {len(matcher.topics)}")
    print(f"• Target ntfy channel:   {notifier.topic}")
    print(f"• History cache size:    {len(cache.seen_ids)} items")
    print("-" * 60)

    all_items = []
    
    # Hugging Face
    if settings.get("enable_sources", {}).get("huggingface_models", True):
        print("🔍 Scanning Hugging Face Hub & Daily Papers...")
        hf = HuggingFaceScout()
        hf_items = hf.fetch_recent_models()
        print(f"   → Found {len(hf_items)} items from Hugging Face.")
        all_items.extend(hf_items)

    # GitHub Releases
    if settings.get("enable_sources", {}).get("github_releases", True):
        print("🔍 Scanning GitHub AI Releases...")
        gh = GitHubScout()
        gh_items = gh.fetch_recent_drops()
        print(f"   → Found {len(gh_items)} releases from GitHub.")
        all_items.extend(gh_items)

    # Reddit LocalLLaMA
    if settings.get("enable_sources", {}).get("reddit_localllama", True):
        print("🔍 Scanning Reddit r/LocalLLaMA...")
        rd = RedditScout()
        rd_items = rd.fetch_recent_drops()
        print(f"   → Found {len(rd_items)} items from Reddit.")
        all_items.extend(rd_items)

    # arXiv AI
    if settings.get("enable_sources", {}).get("arxiv_ai", True):
        print("🔍 Scanning arXiv AI...")
        ax = ArxivScout()
        ax_items = ax.fetch_recent_drops()
        print(f"   → Found {len(ax_items)} preprints from arXiv.")
        all_items.extend(ax_items)

    print("-" * 60)
    print(f"Total raw items gathered: {len(all_items)}. Filtering against your topics...")

    matched_count = 0
    skipped_seen = 0

    for item in all_items:
        item_id = item["id"]
        if cache.is_seen(item_id):
            skipped_seen += 1
            continue

        # Match against user's specific topics
        match = matcher.match(item["title"], item["description"], item.get("tags"))
        
        # Mark as seen so we don't re-scan non-matching items indefinitely
        cache.mark_seen(item_id)

        if match:
            matched_count += 1
            title_str, short_summary, expanded_details = summarizer.format_drop(item, match)

            print(f"\n🚨 [MATCH FOUND] {match['topic_name']}: {item['title']}")
            print(f"   Short (1-2 lines): {short_summary}")

            if dry_run:
                print("   [Dry Run] Skipping notification dispatch.")
            else:
                success = notifier.send_notification(
                    title=title_str,
                    short_summary=short_summary,
                    expanded_details=expanded_details,
                    url=item["url"],
                    priority=match.get("priority", "default")
                )
                if success:
                    print("   ✅ Notification sent to your phone & laptop via ntfy!")
                else:
                    print("   ❌ Failed to send notification.")

    if not dry_run:
        cache.save()
    else:
        print("[Dry Run] Cache was not updated on disk.")
    print("-" * 60)
    print(f"Cycle finished. Skipped seen: {skipped_seen}, New matches alerted: {matched_count}.")
    print("=" * 60)


def cmd_add_topic(name=None, keywords=None, description=None, priority="default"):
    if not os.path.exists(TOPICS_PATH):
        topics_data = {"topics": []}
    else:
        with open(TOPICS_PATH, "r", encoding="utf-8") as f:
            topics_data = json.load(f)

    if not name:
        name = input("Enter Topic Name (e.g. Robotics AI): ").strip()
    if not description:
        description = input("Enter Topic Description (optional): ").strip()
    if not keywords:
        kw_input = input("Enter Keywords (comma-separated, e.g. vla, humanoid, rdt): ").strip()
        keywords_list = [k.strip() for k in kw_input.split(",") if k.strip()]
    else:
        if isinstance(keywords, list):
            keywords_list = keywords
        else:
            keywords_list = [k.strip() for k in keywords.split(",") if k.strip()]

    topic_id = name.lower().replace(" ", "-").replace("/", "-")
    
    new_topic = {
        "id": topic_id,
        "name": name,
        "description": description or f"Tracking {name}",
        "keywords": keywords_list,
        "priority": priority
    }

    # Replace if exists or append
    existing = [t for t in topics_data["topics"] if t.get("id") == topic_id]
    if existing:
        topics_data["topics"] = [t if t.get("id") != topic_id else new_topic for t in topics_data["topics"]]
        print(f"✅ Updated existing topic: '{name}'")
    else:
        topics_data["topics"].append(new_topic)
        print(f"✅ Added new topic permanently: '{name}'")

    with open(TOPICS_PATH, "w", encoding="utf-8") as f:
        json.dump(topics_data, f, indent=2)

    print(f"   Keywords: {', '.join(keywords_list)}")


def cmd_list_topics():
    if not os.path.exists(TOPICS_PATH):
        print("No topics found.")
        return
    with open(TOPICS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    topics = data.get("topics", [])
    print("\n" + "=" * 60)
    print(f"📋 PERSISTENTLY SAVED TOPICS ({len(topics)} active)")
    print("=" * 60)
    for i, t in enumerate(topics, 1):
        print(f"[{i}] {t.get('name')} (ID: {t.get('id')})")
        print(f"    Description: {t.get('description', '')}")
        print(f"    Keywords:    {', '.join(t.get('keywords', []))}")
        print(f"    Priority:    {t.get('priority', 'default')}")
        print("-" * 60)


def cmd_remove_topic(topic_identifier):
    if not os.path.exists(TOPICS_PATH):
        return
    with open(TOPICS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    orig_len = len(data.get("topics", []))
    target = topic_identifier.lower().strip()
    data["topics"] = [
        t for t in data.get("topics", [])
        if t.get("id", "").lower() != target and t.get("name", "").lower() != target
    ]
    if len(data["topics"]) < orig_len:
        with open(TOPICS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"✅ Removed topic: '{topic_identifier}'")
    else:
        print(f"❌ Topic not found: '{topic_identifier}'")


def cmd_test_notification():
    notifier = NtfyNotifier()
    print(f"Sending test notification to ntfy topic: '{notifier.topic}'...")
    title = "🚀 [Test Drop] DeepSeek-R1 Released"
    short_summary = "Open-weights reasoning model matching OpenAI o1 on math and code benchmarks. Apache 2.0 license."
    expanded = (
        "📌 **Model:** DeepSeek-R1\n"
        "🏷️ **Topic:** Reasoning & Thinking Models\n"
        "🌐 **Source:** Hugging Face Hub / GitHub\n\n"
        "⚙️ **Specs & Highlights:**\n"
        "• Parameters: 671B Total (37B active MoE)\n"
        "• License: Apache 2.0\n"
        "• Context Window: 128k tokens\n"
        "• Native GGUF & vLLM support\n\n"
        "🔗 **Weights & Repo:** https://huggingface.co/deepseek-ai/DeepSeek-R1"
    )
    success = notifier.send_notification(
        title=title,
        short_summary=short_summary,
        expanded_details=expanded,
        url="https://huggingface.co/deepseek-ai/DeepSeek-R1",
        priority="high"
    )
    if success:
        print(f"\n🎉 SUCCESS! Test notification pushed successfully.")
        print(f"📱 Check your phone and laptop at: {notifier.server}/{notifier.topic}")
        print("Notice how the notification is 1-2 lines, and expands when clicked/tapped!")
    else:
        print("❌ Failed to push test notification. Check internet connection.")


def cmd_set_channel(channel_name):
    settings = load_settings()
    settings["ntfy_topic"] = channel_name.strip()
    save_settings(settings)
    print(f"✅ ntfy channel updated to: '{channel_name.strip()}'")
    print(f"   Subscribe on your phone/laptop: https://ntfy.sh/{channel_name.strip()}")


def main():
    parser = argparse.ArgumentParser(description="AI News & Model Drops Automation Scout")
    subparsers = parser.add_subparsers(dest="command")

    # run command
    run_parser = subparsers.add_parser("run", help="Run one scout cycle")
    run_parser.add_argument("--dry-run", action="store_true", help="Find drops without sending push notifications")

    # test command
    subparsers.add_parser("test", help="Send a test notification to verify phone & laptop alerts")

    # topic add
    add_parser = subparsers.add_parser("add-topic", help="Add or update a tracked topic")
    add_parser.add_argument("--name", type=str, help="Topic Name")
    add_parser.add_argument("--keywords", type=str, help="Comma-separated keywords")
    add_parser.add_argument("--description", type=str, help="Topic Description")
    add_parser.add_argument("--priority", type=str, default="default", choices=["default", "high", "urgent"])

    # topic list
    subparsers.add_parser("list-topics", help="List all tracked topics")

    # topic remove
    rm_parser = subparsers.add_parser("remove-topic", help="Remove a topic by name or ID")
    rm_parser.add_argument("name", type=str, help="Topic name or ID")

    # set channel
    chan_parser = subparsers.add_parser("set-channel", help="Set custom ntfy topic/channel name")
    chan_parser.add_argument("channel", type=str, help="New ntfy channel name")

    args = parser.parse_args()

    if args.command == "run":
        run_scout_cycle(dry_run=args.dry_run)
    elif args.command == "test":
        cmd_test_notification()
    elif args.command == "add-topic":
        cmd_add_topic(args.name, args.keywords, args.description, args.priority)
    elif args.command == "list-topics":
        cmd_list_topics()
    elif args.command == "remove-topic":
        cmd_remove_topic(args.name)
    elif args.command == "set-channel":
        cmd_set_channel(args.channel)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
