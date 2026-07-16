# 🎙️ Podcast Studio — Content Recapper

**Project 1 — AI Consulting Bootcamp.** An automated podcast generator: give it any lesson,
article, or report (pick a saved one, point it at a public URL, or upload a .txt/.md/.pdf) and it
uses an LLM to pull the key points and text-to-speech to read them back as a short recap episode —
all in a Gradio web app. Built around daily lessons, but works for any readable document.

**Author:** Nnanyelugo Ahukannah

> 🧑‍🎓 **New to GitHub?** Start with **[TEAM_GUIDE.md](TEAM_GUIDE.md)** — a no-terminal, click-by-click
> setup using GitHub Desktop. The steps below are the same thing for people comfortable with a terminal.

---

## 🚀 Getting started (Mac **and** Windows)

> Every teammate uses their **own** OpenAI API key. The app runs locally in your browser.

### 1. Install the prerequisites (one-time)

- **Python 3.10 or newer** — download from [python.org](https://www.python.org/downloads/).
  **Windows users:** on the first install screen, tick **“Add Python to PATH”**.
- **Git** — [git-scm.com](https://git-scm.com/downloads).
- **An OpenAI API key** — sign in at [platform.openai.com](https://platform.openai.com/api-keys),
  create a key, and add a few dollars of credit (this app costs ~1 cent per recap).

### 2. Clone the repo

```bash
git clone https://github.com/nyelugo/PROJECT-Podcast-Studio.git
cd PROJECT-Podcast-Studio
```

### 3. Add your API key

Make your own `.env` file from the template, then paste your key into it.

- **macOS / Linux:** `cp .env.example .env`
- **Windows:** `copy .env.example .env`

Open `.env` in any editor and replace `sk-your-key-here` with your real key. **Never commit `.env`** —
it's already git-ignored.

### 4. Run it — pick ONE of these

**Option A — double-click launcher (easiest):**

- **macOS:** double-click **`run.command`**. (First time only: if macOS says “unidentified developer”,
  right-click the file → **Open** → **Open**.)
- **Windows:** double-click **`run.bat`**.

The launcher creates a virtual environment, installs everything, and opens the app. First run takes a
minute; after that it's instant.

**Option B — run manually in a terminal:**

<details><summary><b>macOS / Linux</b></summary>

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/main.py
```
</details>

<details><summary><b>Windows (PowerShell)</b></summary>

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src\main.py
```
</details>

### 5. Open the app

Go to **http://localhost:7860** in your browser. Pick a saved lesson (or use a public URL / upload a file),
choose a voice, and click **Generate recap podcast**. To stop the app, press `Ctrl+C` in the terminal.

---

## How it works (the pipeline)

```
Lesson (saved file / public URL / uploaded file)  →  LLM key points  →  Text-to-speech  →  Gradio UI
```

- `src/data_processor.py` — cleans the input; can also fetch text from a **public** URL.
- `src/llm_processor.py` — turns it into a structured recap (title, key points, spoken script) with
  OpenAI structured outputs.
- `src/tts_generator.py` — synthesises the script to an `.mp3` (OpenAI TTS).
- `src/main.py` — the Gradio app that ties it together, plus a `--demo` command-line mode.

Add your own lesson files under `input/<something>/…​.txt` and they'll appear in the **Pick a saved
lesson** dropdown next time you launch.

## Project structure

```
PROJECT-Podcast-Studio/
├── src/                     # data_processor, llm_processor, tts_generator, main
├── input/week1/day1…day5/   # saved lesson content (shows up in the picker)
├── output/                  # generated recap audio + scripts
├── run.command / run.bat    # double-click launchers (macOS / Windows)
├── requirements.txt · README.md · .env.example · .gitignore
```

## Troubleshooting

| Problem | Fix |
|---|---|
| **`python` / `python3` not found** | Reinstall Python; on Windows tick “Add to PATH”, then close and reopen the terminal. |
| **PowerShell won't activate the venv** | Run `Set-ExecutionPolicy -Scope Process RemoteSigned` in that window, then activate again. |
| **“No OpenAI API key found”** | Make sure you did step 3 — a `.env` file exists with your real key inside. |
| **macOS: `run.command` “can't be opened”** | Right-click the file → **Open** → **Open** (needed once, for Gatekeeper). |
| **Port 7860 already in use** | Close the other app, or run `GRADIO_SERVER_PORT=7861 python src/main.py` (Windows: `set GRADIO_SERVER_PORT=7861` first). |

## Cost & keys

Each recap makes one LLM call + one TTS call — roughly a cent. Everyone uses their **own** key in their
**own** `.env`; keys are never shared or committed.
