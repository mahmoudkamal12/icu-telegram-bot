import os
import logging
import asyncio
import subprocess
import sys

logger = logging.getLogger(__name__)

async def post_video_to_tiktok(video_path: str, caption: str = "ICU Medical Quiz | Can you answer this? #medicine #ICU #medstudent #clinicalcase #quiz") -> bool:
    """
    Uploads a video to TikTok using the custom Playwright uploader.
    Runs as a separate subprocess to avoid conflicts with the bot's asyncio loop.
    Returns True if successful, False otherwise.
    """
    if not os.path.exists(video_path):
        logger.error(f"Video file not found: {video_path}")
        return False

    script_dir = os.path.dirname(os.path.abspath(__file__))
    cookies_path = os.path.join(script_dir, "cookies.txt")
    uploader_script = os.path.join(script_dir, "custom_tiktok_uploader.py")

    if not os.path.exists(cookies_path):
        logger.error(f"Cookies file not found: {cookies_path}. Please export cookies.txt to this directory.")
        return False

    logger.info(f"[TikTok] Spawning custom upload process for: {os.path.basename(video_path)}")

    try:
        def _run_subprocess():
            result = subprocess.run(
                [sys.executable, uploader_script, video_path, caption],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            return result

        result = await asyncio.to_thread(_run_subprocess)

        if result.returncode == 0:
            logger.info(f"[TikTok] Upload SUCCESS: {os.path.basename(video_path)}")
            if result.stdout.strip():
                logger.info(f"[TikTok] Output: {result.stdout.strip()}")
            return True
        else:
            logger.error(f"[TikTok] Upload FAILED for: {os.path.basename(video_path)}")
            if result.stderr.strip():
                logger.error(f"[TikTok] Error: {result.stderr.strip()}")
            if result.stdout.strip():
                logger.error(f"[TikTok] Output: {result.stdout.strip()}")
            return False

    except Exception as e:
        logger.error(f"[TikTok] Exception during upload: {e}")
        return False
