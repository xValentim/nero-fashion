import argparse
import mimetypes
import time
from google import genai
from google.genai import types
from IPython.display import display
from PIL import Image
from io import BytesIO

import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash-image-preview"

client = genai.Client()

def _load_image_parts(image_paths: list[str]) -> list[Image]:
    """Loads image files and converts them into GenAI Part objects."""
    parts = []
    for image_path in image_paths:
        parts.append(Image.open(image_path))
    return parts

def get_response_and_save_image(response, output_dir: str):

    image_parts = [
        part.inline_data.data
        for part in response.candidates[0].content.parts
        if part.inline_data
    ]

    if image_parts:
        image = Image.open(BytesIO(image_parts[0]))
        image.save(os.path.join(output_dir, 'remixed_image.png'))
    
    return image, os.path.join(output_dir, 'remixed_image.png')

def remix_images(image_paths: list[str], 
                 prompt: str,
                 output_dir: str) -> Image:
    """Remixes the given images based on the text prompt."""
    contents = _load_image_parts(image_paths)
    contents.append(prompt)

    generate_content_config = types.GenerateContentConfig(
        response_modalities=["IMAGE", "TEXT"],
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash-image-preview",
        contents=contents,
        config=generate_content_config
    )


    return get_response_and_save_image(response, output_dir)


