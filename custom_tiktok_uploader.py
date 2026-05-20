"""
custom_tiktok_uploader.py
=========================
A custom Playwright-based TikTok uploader that handles TikTok's
tutorial/joyride overlay which blocks the standard tiktok-uploader library.
"""
import asyncio
import os
import sys
import logging
from pathlib import Path
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

UPLOAD_URL = "https://www.tiktok.com/upload"

async def dismiss_overlays(page):
    """Tries to close any TikTok tutorial / joyride overlay that blocks clicks."""
    try:
        logger.info("Attempting to dismiss any overlays...")
        # Try pressing Escape to close any modal
        await page.keyboard.press("Escape")
        await asyncio.sleep(0.5)
        await page.keyboard.press("Escape")
        
        # Try clicking outside
        await page.mouse.click(10, 10)
        await asyncio.sleep(0.5)

        # Common overlay close/skip buttons
        btn_texts = ["Skip", "Close", "Got it", "Done", "Next", "Not now", "No thanks"]
        for btn_text in btn_texts:
            try:
                btns = page.get_by_role("button", name=btn_text, exact=True)
                count = await btns.count()
                for i in range(count):
                    if await btns.nth(i).is_visible():
                        await btns.nth(i).click()
                        await asyncio.sleep(0.5)
            except Exception:
                pass
                
        # Also try close icons or elements with test-id='overlay'
        try:
            overlay = page.locator("div[data-test-id='overlay']")
            if await overlay.count() > 0:
                await page.keyboard.press("Escape")
                
            close_icons = page.locator("svg[class*='close'], svg[class*='Close'], button[aria-label='Close'], .tiktok-modal-close")
            count = await close_icons.count()
            for i in range(count):
                if await close_icons.nth(i).is_visible():
                    await close_icons.nth(i).click()
                    await asyncio.sleep(0.5)
        except Exception:
            pass
            
    except Exception as e:
        logger.warning(f"Error during overlay dismissal: {e}")

async def upload_to_tiktok(video_path: str, description: str, cookies_path: str, headless: bool = True) -> bool:
    """
    Uploads a video to TikTok using Playwright directly.
    Returns True on success, False on failure.
    """
    if not os.path.exists(video_path):
        logger.error(f"Video file not found: {video_path}")
        return False

    if not os.path.exists(cookies_path):
        logger.error(f"Cookies file not found: {cookies_path}")
        return False

    abs_video_path = str(Path(video_path).resolve())

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context()

        # Load cookies from cookies.txt (Netscape format)
        logger.info("Loading TikTok session cookies...")
        cookies = []
        with open(cookies_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("\t")
                if len(parts) < 7:
                    continue
                domain, _, path, secure, expires, name, value = parts[:7]
                cookies.append({
                    "name": name,
                    "value": value,
                    "domain": domain if domain.startswith(".") else "." + domain,
                    "path": path,
                    "secure": secure.upper() == "TRUE",
                    "expires": int(expires) if expires.isdigit() else -1,
                })

        await context.add_cookies(cookies)
        page = await context.new_page()

        try:
            # Step 1: Navigate to upload page
            logger.info("Navigating to TikTok upload page...")
            await page.goto(UPLOAD_URL, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3)

            # Step 2: Dismiss any tutorial overlays BEFORE doing anything
            await dismiss_overlays(page)

            # Step 3: Upload the video file
            # TikTok's upload page loads the file input inside an iframe
            logger.info(f"Uploading video: {abs_video_path}")
            await asyncio.sleep(2)
            
            # Check if there's an iframe containing the upload UI
            iframe_element = page.frame_locator("iframe").first
            try:
                file_input = iframe_element.locator("input[type='file']")
                await file_input.wait_for(state="attached", timeout=10000)
                logger.info("Found file input inside iframe.")
            except Exception:
                # Fallback: try directly on the page
                logger.info("No iframe found, trying file input directly on page.")
                file_input = page.locator("input[type='file']")
                
            await file_input.set_input_files(abs_video_path)
            logger.info("Video file attached. Waiting for upload to complete...")

            # Step 4: Wait for the video to finish processing (caption field appears)
            # Try inside iframe first, then fallback to page
            try:
                caption_box = iframe_element.locator("div[contenteditable='true']").first
                await caption_box.wait_for(state="visible", timeout=90000)
            except Exception:
                caption_box = page.locator("div[contenteditable='true']").first
                await caption_box.wait_for(state="visible", timeout=90000)
            logger.info("Video processed by TikTok. Setting caption...")

            # Step 5: Dismiss overlays again (they sometimes appear after upload)
            await dismiss_overlays(page)
            await asyncio.sleep(1)

            # Step 6: Click and fill the caption
            await caption_box.click()
            await asyncio.sleep(0.5)
            # Select all and clear existing text
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            await caption_box.type(description, delay=30)
            logger.info("Caption set successfully.")
            await asyncio.sleep(1)

            # Step 7: Click the Post button
            logger.info("Clicking Post button...")
            
            # Dismiss overlays before trying to post (copyright checks, etc.)
            await dismiss_overlays(page)

            try:
                post_button = iframe_element.get_by_role("button", name="Post")
                await post_button.wait_for(state="visible", timeout=10000)
                await post_button.click()
            except Exception:
                try:
                    post_button = page.get_by_role("button", name="Post")
                    await post_button.wait_for(state="visible", timeout=10000)
                    await post_button.click()
                except Exception as post_e:
                    logger.warning(f"Could not find or click standard Post button: {post_e}")
                    
            # Try to force click if still visible after normal click
            await asyncio.sleep(1)
            try:
                if await post_button.is_visible():
                    await post_button.click(force=True)
            except Exception:
                pass

            # Step 8: Wait for confirmation that it posted
            logger.info("Waiting for upload confirmation...")
            
            success = False
            for _ in range(60): # wait up to 60 seconds
                await asyncio.sleep(1)
                url = page.url
                if "creator-center" in url or "profile" in url or "upload" not in url:
                    success = True
                    break
                
                # Check for "View Profile", "Manage your posts", or success toast
                try:
                    manage_posts = page.get_by_role("button", name="Manage your posts")
                    if await manage_posts.count() > 0 and await manage_posts.first.is_visible():
                        success = True
                        break
                        
                    view_profile = page.get_by_role("button", name="View profile")
                    if await view_profile.count() > 0 and await view_profile.first.is_visible():
                        success = True
                        break
                        
                    success_toast = page.locator("text='uploaded'")
                    if await success_toast.count() > 0 and await success_toast.first.is_visible():
                        success = True
                        break
                except Exception:
                    pass
                    
            if success:
                logger.info("SUCCESS: Video posted to TikTok!")
                await browser.close()
                return True
            else:
                raise Exception("Timeout waiting for successful upload confirmation. The Post button may be blocked or the upload failed.")

        except Exception as e:
            logger.error(f"Upload failed: {e}")
            # Save a screenshot to help debug
            try:
                screenshot_path = os.path.join(os.path.dirname(cookies_path), "tiktok_error_screenshot.png")
                await page.screenshot(path=screenshot_path)
                logger.info(f"Screenshot saved for debugging: {screenshot_path}")
            except Exception:
                pass
            await browser.close()
            return False


def main():
    if len(sys.argv) < 3:
        print("Usage: python custom_tiktok_uploader.py <video_path> <caption...>")
        sys.exit(1)

    video_path = sys.argv[1]
    caption = " ".join(sys.argv[2:])
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cookies_path = os.path.join(script_dir, "cookies.txt")

    success = asyncio.run(upload_to_tiktok(video_path, caption, cookies_path, headless=True))
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
