import io
import time
import random
import requests
from PIL import Image
from urllib.parse import quote

MODEL = "flux"  

STYLE_SUFFIX = (
    "digital illustration, storybook art style, vibrant colors, "
    "detailed, cinematic lighting, high quality"
)


def generate_image(prompt: str, width: int = 1024, height: int = 768, retries: int = 3) -> Image.Image:
    """
    Calls Pollinations API to generate an image from a text prompt.
    Uses a random seed per call so each scene gets a unique image.
    Retries on rate-limit and server errors with backoff.
    Returns a PIL Image object. No API key required.
    """
    full_prompt = f"{prompt}, {STYLE_SUFFIX}"
    encoded_prompt = quote(full_prompt, safe="")
    seed = random.randint(1, 2**31 - 1) 

    url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?model={MODEL}&width={width}&height={height}&nologo=true&seed={seed}"
    )

    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=120)
        except requests.exceptions.RequestException as e:
            print(f"Request error on attempt {attempt + 1}: {e}")
            time.sleep(10 * (attempt + 1))
            continue

        if response.status_code in (429, 500, 502, 503):
            wait_time = 10 * (attempt + 1)
            print(f"HTTP {response.status_code} — waiting {wait_time}s before retry...")
            time.sleep(wait_time)
            continue

        response.raise_for_status()

       
        content_type = response.headers.get("Content-Type", "")
        if "image" not in content_type:
            print(f"Unexpected content type: {content_type}. Retrying...")
            time.sleep(10 * (attempt + 1))
            continue

        image = Image.open(io.BytesIO(response.content))
        return image

    raise RuntimeError("Image generation failed after multiple retries.")


def generate_images_for_scenes(scenes: list) -> list:
    """
    Generates images sequentially with a small gap between requests
    to avoid Pollinations rate limiting.
    Returns list of PIL Image objects (or None if a scene failed).
    """
    images = []
    for i, scene in enumerate(scenes):
        print(f"Generating image for scene {i + 1}...")
        try:
            img = generate_image(scene["image_prompt"])
            images.append(img)
            print(f"Scene {i + 1} done.")
        except Exception as e:
            print(f"Scene {i + 1} image failed: {e}")
            images.append(None)

        
        if i < len(scenes) - 1:
            time.sleep(3)

    return images
