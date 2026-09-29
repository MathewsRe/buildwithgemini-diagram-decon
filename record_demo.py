import asyncio
import os
import time
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu"
            ]
        )
        
        # Set up a browser context with video recording enabled
        video_dir = "/config/Desktop/BuildWithGemini/diagram-decon/videos"
        os.makedirs(video_dir, exist_ok=True)
        
        context = await browser.new_context(
            record_video_dir=video_dir,
            record_video_size={"width": 1280, "height": 800},
            viewport={"width": 1280, "height": 800}
        )
        
        page = await context.new_page()
        
        print("Navigating to frontend...")
        await page.goto("http://localhost:8080", wait_until="networkidle")
        await asyncio.sleep(2)
        
        # Prompt 1: Core functionality - Deconstruct architecture diagram into modular components
        prompt1 = "Deconstruct an e-commerce cloud architecture (Web Frontend, API Gateway, Order Service, and Cloud Database) into modular diagram blocks."
        print(f"Typing prompt 1: {prompt1}")
        await page.fill("#input", prompt1)
        await asyncio.sleep(1)
        await page.click("#send-btn")
        
        # Wait for agent response (poll until placeholder '…' disappears)
        print("Waiting for response 1...")
        for _ in range(60):
            await asyncio.sleep(1)
            bubbles = await page.query_selector_all(".msg.agent .bubble")
            if bubbles:
                last_bubble = bubbles[-1]
                text = await last_bubble.inner_text()
                if text.strip() and text.strip() != "…":
                    print("Received response 1!")
                    break
        
        await asyncio.sleep(4)
        
        # Prompt 2: Richer prompt with tool calls - Firestore lookup, icon search, and SVG publication
        prompt2 = "Save the Order Service block to Firestore with tags ['backend', 'microservice'], search for a shopping cart icon from Iconify, and publish the assembled SVG diagram to Google Cloud Storage."
        print(f"Typing prompt 2: {prompt2}")
        await page.fill("#input", prompt2)
        await asyncio.sleep(1)
        await page.click("#send-btn")
        
        print("Waiting for response 2...")
        for _ in range(75):
            await asyncio.sleep(1)
            bubbles = await page.query_selector_all(".msg.agent .bubble")
            if len(bubbles) >= 2:
                last_bubble = bubbles[-1]
                text = await last_bubble.inner_text()
                if text.strip() and text.strip() != "…":
                    print("Received response 2!")
                    break
        
        await asyncio.sleep(5)
        
        # Close context to save the recorded video
        await context.close()
        await browser.close()
        print("Recording complete!")

if __name__ == "__main__":
    asyncio.run(main())
