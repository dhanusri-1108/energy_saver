# EnergySaver AI

Electricity usage & energy-saving suggestions

Flask backend — your API key lives in `.env` on your machine and never
reaches the browser.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and paste your key:

```
ANTHROPIC_API_KEY=sk-ant-your-real-key-here
```

Get a key at https://console.anthropic.com/settings/keys

## Run

```bash
python app.py
```

Open http://127.0.0.1:5008 in your browser.

## Files

- `app.py` — Flask server; calls the Anthropic API server-side using your `.env` key
- `templates/index.html` — page layout
- `static/style.css` — this bot's look (accent color: #B08900)
- `static/script.js` — talks to our own `/api/chat` endpoint (never touches the key)
- `requirements.txt` — Python dependencies
- `.env.example` — copy to `.env` and fill in your key

## Editing the personality

Open `app.py` and edit the `SYSTEM_PROMPT` variable near the top.
