import os
import base64
import urllib.parse
import asyncio
import shutil
from fastapi import FastAPI, HTTPException
from playwright.async_api import async_playwright
from starlette.responses import FileResponse

app = FastAPI()

class RaySoImageGenerator:
    def __init__(self):
        self.output_dir = os.getcwd()

    def encode_code_for_ray(self, code: str) -> str:
        """Encodes a code snippet to be used in a Ray.so URL."""
        base64_code = base64.b64encode(code.encode()).decode()
        return urllib.parse.quote(base64_code)

    async def generate_image(self, code: str) -> str:
        """Processes the given Python code and generates an image."""
        encoded_code = self.encode_code_for_ray(code)
        url = f"https://ray.so/#padding=64&theme=vercel&code={encoded_code}&darkMode=true&language=auto&background=true"

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(accept_downloads=True)
            page = await context.new_page()

            await page.goto(url, wait_until="networkidle")

            await page.wait_for_selector("span:has-text('Export')")
            async with page.expect_download() as download_info:
                await page.click("span:has-text('Export')")

            download = await download_info.value
            downloaded_path = await download.path()

            image_filename = "generated_code.png"
            new_path = os.path.join(self.output_dir, image_filename)
            shutil.move(downloaded_path, new_path)

            await browser.close()
            return new_path

@app.get("/")
def home():
    return {"message": "Welcome to RaySo API. Use /generate?code=your_code to generate an image."}

@app.get("/generate")
async def generate_image(code: str):
    """Accepts a GET request with a code snippet and returns an image."""
    if not code:
        raise HTTPException(status_code=400, detail="Code parameter is required")

    generator = RaySoImageGenerator()
    image_path = await generator.generate_image(code)
    
    if image_path:
        return FileResponse(image_path, media_type="image/png", filename="code_image.png")
    else:
        raise HTTPException(status_code=500, detail="Image generation failed")