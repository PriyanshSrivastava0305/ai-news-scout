# 🤖 AI News & Model Drop Scout (24/7 Automation)

An automated scouting engine that monitors the AI landscape 24/7 for new model releases, open-source weights, and breakthroughs matching **your exact specified topics**.

Sends instant notifications to your **phone and laptop** in a **1–2 line preview** that expands into a full dossier on tap.

---

## ⚡ Quick Start: Receive Alerts on Phone & Laptop

Your unique notification channel is:
```text
https://ntfy.sh/ai-news-scout-alert-94b2f1
```
*(You can change this anytime with `python scout.py set-channel <your-name>`)*

### 📱 1. On Your Phone (iOS & Android)
1. Install **ntfy** from the [Google Play Store](https://play.google.com/store/apps/details?id=io.heckel.ntfy) or [Apple App Store](https://apps.apple.com/app/ntfy/id1625396347).
2. Open the app, tap **+ (Subscribe to topic)**.
3. Enter your topic name: `ai-news-scout-alert-94b2f1`.
4. Done! You will now receive instant push alerts with sound.

### 💻 2. On Your Laptop (Windows / macOS / Linux)
1. Open [`https://ntfy.sh/ai-news-scout-alert-94b2f1`](https://ntfy.sh/ai-news-scout-alert-94b2f1) in your browser.
2. Click **Subscribe to topic** at the top right and allow browser notifications.
3. You will now get native OS notifications on your desktop!

### 🔔 3. Test Your Alerts Now
From this project directory, run:
```bash
python scout.py test
```
Both your phone and laptop will instantly ring with a sample 1–2 line alert. Click or tap to expand the full dossier!

---

## 🎯 Managing Your Topics (Saved Forever)

All your topics are permanently stored in [`config/topics.json`](config/topics.json). You can edit the file directly or use the CLI:

### View active topics:
```bash
python scout.py list-topics
```

### Add a new topic:
```bash
python scout.py add-topic --name "Robotics AI" --keywords "vla, humanoid, rdt, openvla, lerobot" --description "Embodied AI and robotics models" --priority high
```

### Remove a topic:
```bash
python scout.py remove-topic "Robotics AI"
```

---

## 🌐 24/7 Cloud Deployment (GitHub Actions - 100% Free)

This repository includes a pre-configured GitHub Actions workflow ([`.github/workflows/scout.yml`](.github/workflows/scout.yml)) that runs **every 30 minutes in the cloud 24/7**, completely independent of your laptop being on or off.

### Setup Instructions:
1. Initialize Git and create a repository on GitHub (Private or Public):
   ```bash
   git init
   git add .
   git commit -m "Initial commit of AI News Scout"
   git branch -M main
   git remote add origin https://github.com/<your-username>/ai-news-scout.git
   git push -u origin main
   ```
2. Enable Workflow Permissions:
   - On GitHub, go to **Settings** → **Actions** → **General**.
   - Under **Workflow permissions**, select **Read and write permissions** (this allows the bot to persist the seen cache so you never get duplicate alerts).
   - Click **Save**.
3. (Optional) Custom Channel or Gemini Summarizer:
   - Go to **Settings** → **Secrets and variables** → **Actions** to add:
     - `NTFY_TOPIC`: Your private channel name.
     - `GEMINI_API_KEY`: (Optional) Free Google Gemini API key for advanced AI synthesis.

Once pushed, GitHub Actions will run automatically around the clock!

---

## 🏗️ Architecture

```
                               ┌───────────────────────────┐
                               │   Scout Engine (24/7)     │
                               │  - Hugging Face Models    │
                               │  - HF Daily Papers        │
                               │  - GitHub AI Releases     │
                               │  - Reddit r/LocalLLaMA    │
                               │  - arXiv Preprints        │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │     Topic Matcher         │
                               │ Reads config/topics.json  │
                               │ (Filtered & Deduplicated) │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │     1-2 Line Formatter    │
                               │ Crisp preview + full spec │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                             ┌───────────────────────────────┐
                             │    ntfy.sh Push Dispatcher    │
                             └───────┬───────────────┬───────┘
                                     │               │
                                     ▼               ▼
                              📱 Phone Push   💻 Laptop Desktop
                              (1-2 Lines)      (Expand on click)
```

---

## 🛠️ CLI Reference

| Command | Description |
| :--- | :--- |
| `python scout.py run` | Runs a single scouting pass across all sources |
| `python scout.py run --dry-run` | Runs a pass and logs matches without sending notifications |
| `python scout.py test` | Sends a formatted test alert to verify phone & laptop push |
| `python scout.py list-topics` | Prints all permanently saved topics and keywords |
| `python scout.py add-topic` | Adds a new topic interactively or via flags |
| `python scout.py remove-topic <id>` | Removes a topic from monitoring |
| `python scout.py set-channel <name>` | Updates the ntfy channel name |
