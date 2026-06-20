# 📖 Story Illustrator

An AI-powered interactive storybook generator. Enter a theme, and the app writes a 4-scene story using a Large Language Model, then illustrates each scene using a Diffusion Model — all displayed in an interactive Gradio interface.

---

## System Architecture

```
User Prompt
    │
    ▼
[Gradio UI]
    │
    ▼
[LLM — Big Pickle via OpenRouter]
  Generates 4-scene structured story
    │
    ▼
[Scene Parser]
  Extracts narrative text + image prompt per scene
    │
    ▼
[Diffusion Model — FLUX.1-schnell via HuggingFace]
  Generates one illustration per scene
    │
    ▼
[Gradio UI — Story Display]
  Shows title, scene text, and image side by side
```

**Technologies used:**
- **LLM:** `opencode/big-pickle` (Zhipu GLM-4.6, 355B MoE) via OpenRouter
- **Diffusion:** `black-forest-labs/FLUX.1-schnell` via HuggingFace Inference API
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

### 3. Set up API keys
```bash
cp .env.example .env
```
Then open `.env` and fill in:
```
OPENROUTER_API_KEY=sk-or-your-key-here
HF_TOKEN=hf_your-token-here
```

**Getting your keys:**
- OpenRouter: sign up at [openrouter.ai](https://openrouter.ai) → Keys → Create Key
- HuggingFace: sign up at [huggingface.co](https://huggingface.co) → Settings → Access Tokens → New Token (Read)
- Also accept the FLUX.1-schnell license at: [huggingface.co/black-forest-labs/FLUX.1-schnell](https://huggingface.co/black-forest-labs/FLUX.1-schnell)

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
├── llm_client.py       # OpenRouter / Big Pickle API integration
├── image_client.py     # HuggingFace FLUX.1-schnell integration
├── requirements.txt    # Python dependencies
├── .env.example        # API key template
├── .env                # Your API keys (never commit this)
└── README.md
```

---

## Features

- 🖊️ **LLM story generation** with structured scene parsing
- 🎨 **Diffusion image generation** with storybook-style prompts
- 📖 **Interactive Gradio UI** with 4-scene storybook layout
- 💡 **Example prompts** to get started quickly
- 📥 **Downloadable images** for each scene

---

## Notes

- First image generation may take ~20–30 seconds if the model is cold-loading on HuggingFace.
- The Big Pickle model has a 200k context window — complex prompts are fully supported.
- All inference is API-based; no local GPU required.
