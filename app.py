import os
import gradio as gr
from dotenv import load_dotenv
load_dotenv() 

from llm_client import generate_story
from image_client import generate_images_for_scenes

EXAMPLES = [
    "A kitten explores a garden",
    "A young penguin learns how to swim",
    "A small dragon learns to bake cookies",
    "A child who discovers a hidden door",
]

CSS = """
#title-box { text-align: center; margin-bottom: 8px; }
#story-title { font-size: 1.6rem; font-weight: 600; margin: 0; }
.scene-card { border: 1px solid var(--border-color-primary); border-radius: 12px; padding: 16px; margin-bottom: 12px; }
.scene-label { font-weight: 600; font-size: 0.85rem; color: var(--body-text-color-subdued); margin-bottom: 6px; }
"""


def run_pipeline(user_prompt: str, progress=gr.Progress()):
    """
    Full pipeline: prompt → story → images → display
    """
    if not user_prompt.strip():
        raise gr.Error("Please enter a story theme or prompt!")

    # Step 1: Generate story
    progress(0.1, desc="✍️  Writing your story...")
    try:
        story_data = generate_story(user_prompt)
    except Exception as e:
        raise gr.Error(f"Story generation failed: {e}")

    title = story_data["title"]
    scenes = story_data["scenes"]

    progress(0.3, desc="🎨  Illustrating scenes (this takes ~150s)...")

    # Step 2: Generate images 
    try:
        images = generate_images_for_scenes(scenes)
    except Exception as e:
        raise gr.Error(f"Image generation failed: {e}")

    progress(0.95, desc="📖  Assembling your storybook...")

    # Step 3: Build outputs 
    scene_texts = [s["story"] for s in scenes]
    valid_images = [img if img is not None else None for img in images]

    progress(1.0, desc="✅  Done!")
    return (
        title,
        valid_images[0], scene_texts[0],
        valid_images[1], scene_texts[1],
        valid_images[2], scene_texts[2],
        valid_images[3], scene_texts[3],
    )


# UI Layout 
with gr.Blocks(title="Story Illustrator") as demo:

    gr.HTML("""
        <div id="title-box">
            <p id="story-title">📖 Story Illustrator</p>
            <p style="color: gray; font-size: 0.95rem; margin-top: 4px;">
                Enter a theme and watch AI write and illustrate your story.
            </p>
        </div>
    """)

    with gr.Row():
        with gr.Column(scale=4):
            prompt_input = gr.Textbox(
                placeholder="e.g. A lonely robot who learns to paint...",
                label="Story theme or prompt",
                lines=2
            )
        with gr.Column(scale=1, min_width=120):
            generate_btn = gr.Button("✨ Generate", variant="primary", size="lg")

    gr.Examples(
        examples=EXAMPLES,
        inputs=prompt_input,
        label="Try an example"
    )

    # Story title output
    story_title_out = gr.Textbox(label="Story Title", interactive=False, visible=True)

    gr.Markdown("---")

    # 4 scene cards
    scene_outputs = []
    with gr.Row():
        for i in range(2):
            with gr.Column():
                img = gr.Image(label=f"Scene {i+1}")
                txt = gr.Textbox(label=f"Scene {i+1} text", lines=3, interactive=False)
                scene_outputs.extend([img, txt])

    with gr.Row():
        for i in range(2, 4):
            with gr.Column():
                img = gr.Image(label=f"Scene {i+1}")
                txt = gr.Textbox(label=f"Scene {i+1} text", lines=3, interactive=False)
                scene_outputs.extend([img, txt])

    # Wire up
    generate_btn.click(
        fn=run_pipeline,
        inputs=[prompt_input],
        outputs=[story_title_out] + scene_outputs,
    )

    gr.Markdown(
        "<center><small>Powered by Llama 3.1 8B via Groq + FLUX via Pollinations</small></center>"
    )

if __name__ == "__main__":
    demo.launch(share=False, show_error=True, theme=gr.themes.Soft())
