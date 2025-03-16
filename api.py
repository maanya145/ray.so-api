import os
import base64
import urllib.parse
import asyncio
import shutil
import logging
from fastapi import FastAPI, Query, HTTPException
from playwright.async_api import async_playwright
from playwright.__main__ import main

# Ensure Playwright browsers are installed
main(["install"])

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

class RaySoImageGenerator:
    def __init__(self):
        self.output_dir = os.getcwd()

    def encode_code_for_ray(self, code: str) -> str:
        base64_code = base64.b64encode(code.encode()).decode()
        return urllib.parse.quote(base64_code)

    async def generate_image(self, code: str) -> str:
        encoded_code = self.encode_code_for_ray(code)
        url = f"https://ray.so/#padding=64&theme=vercel&code={encoded_code}&darkMode=true&language=auto&background=true"

        try:
            async with async_playwright() as p:
                logger.debug("Launching browser...")
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(accept_downloads=True)
                page = await context.new_page()

                logger.debug(f"Navigating to: {url}")
                await page.goto(url, wait_until="networkidle")

                await page.wait_for_selector("span:has-text('Export')")
                async with page.expect_download() as download_info:
                    await page.click("span:has-text('Export')")

                download = await download_info.value
                downloaded_path = await download.path()

                image_filename = "test_code_image.png"
                new_path = os.path.join(self.output_dir, image_filename)
                shutil.move(downloaded_path, new_path)

                await browser.close()
                logger.debug(f"Image saved at: {new_path}")
                return new_path

        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return None

@app.get("/")
def read_root():
    return {"message": "Welcome to RaySo API. Use /generate?code=your_code to generate an image."}

@app.get("/generate")
async def generate_image(code: str = Query(..., description="Python code to generate an image")):
    generator = RaySoImageGenerator()
    image_path = await generator.generate_image(code)

    if not image_path:
        raise HTTPException(status_code=500, detail="Failed to generate image.")

    return {"image_path": image_path}
