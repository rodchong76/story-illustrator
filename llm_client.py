import os
import re as _re
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_ID = "llama-3.1-8b-instant"

# ── Prompts ───────────────────────────────────────────────────────────────────

STORY_SYSTEM_PROMPT = """You are a creative storyteller. When given a theme or prompt, you write a short illustrated story with exactly 4 scenes.

Format your response EXACTLY like this (do not deviate):

TITLE: [Story Title]

SCENE 1:
STORY: [2-3 sentences of narrative text, all on ONE line]
IMAGE: [A vivid, detailed visual description of this scene for an image generator. All on ONE line.]

SCENE 2:
STORY: [2-3 sentences of narrative text, all on ONE line]
IMAGE: [A vivid, detailed visual description of this scene for an image generator. All on ONE line.]

SCENE 3:
STORY: [2-3 sentences of narrative text, all on ONE line]
IMAGE: [A vivid, detailed visual description of this scene for an image generator. All on ONE line.]

SCENE 4:
STORY: [2-3 sentences of narrative text, all on ONE line]
IMAGE: [A vivid, detailed visual description of this scene for an image generator. All on ONE line.]

IMPORTANT: Each STORY: and IMAGE: value must be on a single line. Do not use line breaks inside them.
Do NOT use markdown formatting such as ** or __ anywhere in your response.
Keep the story engaging, imaginative, and suitable for all ages."""

VISUAL_BIBLE_PROMPT = """You are a visual art director for a children's storybook.
Given a story theme, output a single compact line (under 60 words) describing:
1. The main character's appearance (species, size, colors, one distinctive accessory)
2. The art style (e.g. "watercolor storybook illustration")
3. The color palette (2-3 dominant colors)

Reply with ONLY that one line. No labels, no bullet points, no markdown.

Example output:
a small orange fox with bright amber eyes and a tiny blue scarf, watercolor storybook illustration, warm amber and forest green palette

Story theme: {user_prompt}"""

TITLE_FALLBACK_PROMPT = (
    "Read the following story and reply with ONLY a short, creative title for it "
    "(3-6 words, no quotes, no punctuation at the end):\n\n{story_text}"
)


# API helpers 

def _call_groq(messages: list, max_tokens: int, headers: dict) -> str:
    """Single reusable Groq API call. Returns the text content."""
    payload = {
        "model": MODEL_ID,
        "max_tokens": max_tokens,
        "messages": messages,
    }
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def _build_headers() -> dict:
    return {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }


# Public API
def generate_story(user_prompt: str) -> dict:
    """
    Full pipeline:
      1. Generate a visual bible (character + style + palette) for the story.
      2. Generate the 4-scene story with IMAGE prompts.
      3. Inject the visual bible into every scene's image_prompt for consistency.
    Returns a dict: { "title": str, "scenes": [...], "visual_bible": str }
    """
    headers = _build_headers()

    # Step 1: Visual bible
    try:
        visual_bible = _call_groq(
            messages=[{"role": "user", "content": VISUAL_BIBLE_PROMPT.format(user_prompt=user_prompt)}],
            max_tokens=80,
            headers=headers,
        ).strip().strip('"\'')
    except Exception:
        visual_bible = "storybook watercolor illustration, vibrant colors, warm palette"

    # Step 2: Story generation 
    raw_text = _call_groq(
        messages=[
            {"role": "system", "content": STORY_SYSTEM_PROMPT},
            {"role": "user", "content": f"Write a story about: {user_prompt}"},
        ],
        max_tokens=1500,
        headers=headers,
    )
    result = parse_story(raw_text)

    # ── Step 3: Inject visual bible into every image prompt 
    for scene in result["scenes"]:
        scene_action = scene.get("image_prompt", "").strip()
        scene["image_prompt"] = f"{visual_bible} — {scene_action}"

    # Fallback title
    if result["title"] == "Untitled Story" and result["scenes"]:
        story_text = " ".join(s["story"] for s in result["scenes"] if s.get("story"))
        try:
            raw_title = _call_groq(
                messages=[{"role": "user", "content": TITLE_FALLBACK_PROMPT.format(story_text=story_text)}],
                max_tokens=20,
                headers=headers,
            ).strip()
            result["title"] = _re.sub(r'^["\']|["\']$', '', raw_title).strip()
        except Exception:
            pass

    result["visual_bible"] = visual_bible
    return result


# Parser 

def _clean(line: str) -> str:
    """Strip markdown bold/italic markers and leading # headers."""
    line = _re.sub(r'\*{1,2}|_{1,2}', '', line)
    line = _re.sub(r'^#+\s*', '', line)
    return line.strip()


def parse_story(raw_text: str) -> dict:
    """
    Parses structured LLM output into:
    { "title": str, "scenes": [{"story": str, "image_prompt": str}, ...] }
    Robust to markdown bold, scene subtitles, multi-line values.
    """
    lines = raw_text.strip().split("\n")
    title = "Untitled Story"
    title_found = False
    scenes = []
    current_scene = {}
    current_field = None

    for line in lines:
        raw_stripped = line.strip()
        stripped = _clean(raw_stripped)
        if not stripped:
            continue

        upper = stripped.upper()

        if upper.startswith("TITLE:"):
            title = stripped[6:].strip().strip('"\'')
            title_found = True
            current_field = None

        elif raw_stripped.startswith("#") and not title_found and not scenes and not current_scene:
            title = stripped.strip('"\'')
            title_found = True
            current_field = None

        elif _re.match(r'^SCENE\s+\d+', stripped, _re.IGNORECASE):
            if current_scene:
                scenes.append(current_scene)
            current_scene = {"story": "", "image_prompt": ""}
            current_field = None

        elif upper.startswith("STORY:"):
            current_field = "story"
            current_scene["story"] = stripped[6:].strip()

        elif upper.startswith("IMAGE:"):
            current_field = "image_prompt"
            current_scene["image_prompt"] = stripped[6:].strip()

        elif current_field and current_scene:
            current_scene[current_field] += " " + stripped

    if current_scene and (current_scene.get("story") or current_scene.get("image_prompt")):
        scenes.append(current_scene)

    while len(scenes) < 4:
        scenes.append({
            "story": "The story continues...",
            "image_prompt": "A beautiful fantasy landscape, digital art, detailed"
        })

    return {"title": title, "scenes": scenes[:4]}
