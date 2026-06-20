# Agent Collaboration Log — Story Illustrator

**Course:** Deep Generative Models
**Project:** Story Illustrator
**Agent Used:** Claude (Anthropic) via claude.ai

---

## Phase 1: Ideation and Planning

### Prompt used
> "Based on my previous homework, I want to build a Story Illustrator for my Deep Generative Models final project. What hardware requirements would it need, and what's the most efficient way to build it?"

### Agent output
The agent confirmed that *Story Illustrator* — a creative app where users enter a story theme, the LLM writes a 4-scene story, and a diffusion model illustrates each scene — was a strong fit to demonstrate the semester's material, since it combines both an LLM and a diffusion model in one pipeline.

The agent proposed two API-based options so no local GPU would be required:
1. **Big Pickle (GLM-4.6) via OpenRouter + FLUX.1-schnell via HuggingFace** — free tier, but subject to credit limits
2. **Llama 3.1 8B Instant via Groq + FLUX via Pollinations** — free and effectively unlimited

I chose **option 2** because of the unlimited usage, which matters for repeated testing during development.

**Technology stack decided:**
- LLM: Llama 3.1 8B Instant via Groq — free tier, very fast inference, no credit limits
- Diffusion: FLUX via the Pollinations image API — free, no API key, no local GPU, no credit limits
- UI: Gradio — fast to build, suitable for demos

**Why this stack:** Fully API-based inference means zero local GPU memory usage. Both technologies are required by the assignment. The creative domain makes for a visually compelling demo.

---

## Phase 2: Architecture Design and Task Decomposition

### Prompt used
> "Create a simple architecture for the Story Illustrator app."

### Agent output
The agent produced a simple, linear pipeline architecture:

1. Gradio UI (user enters a theme)
2. LLM API generates the 4-scene story
3. Scene Parser splits each scene into story text + image prompt
4. Diffusion API generates one illustration per scene
5. Gradio UI displays the title, scene text, and image for each scene

**Task decomposition:**
- `llm_client.py` — wrap the Groq API, generate a visual bible for character/style consistency, include structured story prompt, parse output
- `image_client.py` — wrap the Pollinations image API, handle retries for rate limits/cold starts
- `app.py` — Gradio layout, wire pipeline together
- `requirements.txt`, `.env.example`, `README.md`

**Key architectural decision:** The LLM is prompted with a strict output format (`SCENE N: / STORY: / IMAGE:`) so the scene parser can reliably split story text from image prompts without complex NLP. A separate short "visual bible" call (character appearance, art style, palette) is generated first and prepended to every scene's image prompt, keeping the illustrations visually consistent across scenes.

---

## Phase 3: Code Generation and Implementation

### Prompt used
> "Here are my `llm_client.py`, `image_client.py`, and `app.py` files — I wrote these myself. Can you help me find the technical bottlenecks?"

### Files reviewed (authored by student)
| File | Description |
|------|-------------|
| `llm_client.py` | Groq API call, visual bible step, system prompt, story parser, title fallback |
| `image_client.py` | Pollinations FLUX call, retry logic, PIL image return |
| `app.py` | Full Gradio UI, progress bar, 4-scene layout, example prompts |
| `requirements.txt` | `gradio`, `requests`, `Pillow`, `python-dotenv` |
| `.env.example` | API key template |

### Technical bottleneck resolved
**Problem:** The Pollinations image API can return rate-limit or server errors (HTTP 429/500/502/503) under load.
**Solution:** The agent added a retry loop in `image_client.py` with linear backoff (`10s × attempt`) before retrying, up to 3 attempts per scene, plus a small delay between scenes to avoid tripping rate limits in the first place.

**Problem:** LLM output formatting can be inconsistent.
**Solution:** The agent added a `parse_story()` fallback that fills missing scenes with placeholder content, and a separate title-fallback call if no `TITLE:` line is found, preventing the UI from breaking if the LLM deviates from the format.

---

## Phase 4: Interface Encapsulation and Finalization

### Prompt used
> "Generate the README.md and workflow log."

### Agent output
- `README.md` with architecture overview, setup instructions, project structure
- `workflow_log.md` (this file)

### UI decisions made with agent assistance
- Used `gr.Progress()` for real-time progress feedback during the pipeline
- 2×2 grid layout for the 4 scenes (image + text per scene)
- Example prompts added for demo convenience
- Soft Gradio theme for clean visual presentation

---

## Summary of Tools Used

| Tool | Purpose |
|------|---------|
| Claude (claude.ai) | Architecture design, code generation, documentation |
| Groq | LLM API gateway to Llama 3.1 8B Instant |
| Llama 3.1 8B Instant | Visual bible generation, story generation, title fallback |
| Pollinations | Image generation (FLUX) |
| Gradio | Interactive UI framework |
| python-dotenv | Secure API key management |

---

## Key Prompts Summary

1. *"Based on my previous homework, I want to build a Story Illustrator for my Deep Generative Models final project. What hardware requirements would it need, and what's the most efficient way to build it?"*
2. *"Create a simple architecture for the Story Illustrator app."*
3. *"Here are my `llm_client.py`, `image_client.py`, and `app.py` files — I wrote these myself. Can you help me find the technical bottlenecks?"*
4. *"Generate the README and workflow log."*
