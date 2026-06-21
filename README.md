# 📖 Story Illustrator

An AI-powered interactive storybook generator. Enter a theme, and the app writes a 4-scene story using a Large Language Model, then illustrates each scene using a Diffusion Model, all displayed in an interactive Gradio interface.

---

## System Architecture

```
User Prompt
    │
    ▼
[Gradio UI]
    │
    ▼
[LLM — Llama 3.1 8B Instant via Groq]
  Generates a visual bible + 4-scene structured story
    │
    ▼
[Scene Parser]
  Extracts narrative text + image prompt per scene
  (visual bible injected into each image prompt for character consistency)
    │
    ▼
[Diffusion Model — FLUX via Pollinations]
  Generates one illustration per scene (with retry/backoff for rate limits)
    │
    ▼
[Gradio UI — Story Display]
  Shows title, scene text, and image side by side
```

**Technologies used:**
- **LLM:** `llama-3.1-8b-instant` via the Groq API
- **Diffusion:** `flux` via the Pollinations image API (no API key required)
- **UI:** Gradio 4.x
- **Language:** Python 3.10+

---

## Local Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/your-username/story-illustrator.git
cd story-illustrator
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up API key
```bash
```
Open .env and fill in:
```
GROQ_API_KEY=gsk_your-key-here
```

**Getting your key:**
- Groq: sign up at [console.groq.com](https://console.groq.com) → API Keys → Create API Key

> Note: Image generation uses the public Pollinations API and does not require an API key.

### 4. Run the app
```bash
python app.py
```
Then open your browser at `http://127.0.0.1:7860`

---

## Project Structure

```
story-illustrator/
├── app.py              # Gradio UI and main pipeline
├── llm_client.py       # Groq / Llama 3.1 8B Instant integration
├── image_client.py     # Pollinations FLUX integration
├── requirements.txt    # Python dependencies
├── .env                
└── README.md
```

---

## Features

- 🖊️ **LLM story generation** with a visual bible step for consistent characters/style, plus structured scene parsing
- 🎨 **Diffusion image generation** with storybook-style prompts 
- 📖 **Interactive Gradio UI** with 4-scene storybook layout
- 💡 **Example prompts** to get started quickly

---

## Notes

- Image generation may need a few retries if Pollinations is rate-limited; the client backs off automatically (up to 3 attempts per scene).
- All inference is API-based; no local GPU required.
