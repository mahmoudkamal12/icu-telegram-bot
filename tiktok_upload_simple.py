import sys
import os
from tiktok_uploader.upload import upload_video

def main():
    if len(sys.argv) < 3:
        print("Usage: python tiktok_upload_simple.py <video_path> <caption...>")
        return

    video_path = sys.argv[1]
    caption = " ".join(sys.argv[2:])
    
    # Force cookies.txt to be in the same folder as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cookies_path = os.path.join(script_dir, "cookies.txt")

    if not os.path.exists(video_path):
        print(f"❌ Error: Video file not found at {video_path}")
        sys.exit(1)

    if not os.path.exists(cookies_path):
        print(f"❌ Error: Cookies file not found at {cookies_path}")
        sys.exit(1)

    try:
        failed_videos = upload_video(
            video_path,
            description=caption,
            cookies=cookies_path, 
            headless=False  # Set to False so we can see what's getting stuck!
        )
        
        if len(failed_videos) == 0:
            print("✅ Video uploaded successfully!")
            sys.exit(0)
        else:
            print("❌ Upload failed.")
            sys.exit(1)
            
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
