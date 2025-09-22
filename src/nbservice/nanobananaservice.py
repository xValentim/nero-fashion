# from    fastmcp import FastMCP
from mcp.server.fastmcp import FastMCP
import asyncio, platform
from datetime import datetime
import bs4
from langchain_community.document_loaders import WebBaseLoader
from utils import *

# if platform.system() == "Windows":
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

mcp = FastMCP()

@mcp.tool()
def add(a: int, b: int) -> int:
    """Adds two numbers."""
    return a + b

@mcp.tool()
def remix_images_tool(image_paths: list[str], 
                      prompt: str) -> str:
    """Remixes the given images based on the text prompt."""
    output_dir = "./output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    if not prompt:
        prompt = "Mix the images together in a creative way."
        
    image, image_path = remix_images(image_paths, 
                                     prompt, 
                                     output_dir)
    display(image)
    return image_path

if __name__ == "__main__":
    # Start an HTTP server on port 8000
    # mcp.run(transport="http", port=8000, path="/mcp")
    mcp.run(transport="streamable-http")