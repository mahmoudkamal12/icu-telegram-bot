import os
import asyncio
import edge_tts
import uuid
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import logging

# Set up logging for video generation
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Suppress moviepy verbose output if possible
os.environ["IMAGEIO_FFMPEG_EXE"] = "ffmpeg"

def create_3d_background(width, height, center_color, edge_color):
    """Creates a 3D spotlight radial gradient using NumPy for speed."""
    x = np.arange(width)
    y = np.arange(height)
    X, Y = np.meshgrid(x, y)
    
    cx, cy = width / 2, height / 2
    max_dist = np.sqrt(cx**2 + cy**2)
    
    dist = np.sqrt((X - cx)**2 + (Y - cy)**2)
    ndist = np.clip(dist / max_dist, 0, 1)
    
    # Create a curved falloff for a realistic spotlight 3D effect
    mask = 1 - (ndist ** 1.3)
    
    r = (center_color[0] * mask + edge_color[0] * (1 - mask)).astype(np.uint8)
    g = (center_color[1] * mask + edge_color[1] * (1 - mask)).astype(np.uint8)
    b = (center_color[2] * mask + edge_color[2] * (1 - mask)).astype(np.uint8)
    
    return Image.fromarray(np.stack([r, g, b], axis=-1))

def draw_text_with_word_wrap(draw, text, max_width, font, fill=(255, 255, 255), highlight_idx=-1, highlight_color=(255, 255, 0)):
    """Word wraps text and draws it with a 3D extrusion effect, returning the height used."""
    lines = []
    paragraphs = text.split('\n')
    word_idx = 0
    
    for paragraph in paragraphs:
        if not paragraph.strip():
            lines.append([])
            continue
        words = paragraph.split(' ')
        current_line = []
        for w in words:
            if not w: continue
            # Check width
            test_line = " ".join([cw[0] for cw in current_line] + [w])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            w_px = bbox[2] - bbox[0]
            if w_px > max_width and len(current_line) > 0:
                lines.append(current_line)
                current_line = [(w, word_idx)]
            else:
                current_line.append((w, word_idx))
            word_idx += 1
        if current_line:
            lines.append(current_line)
    
    y_offset = 0
    depth = 6 # 3D extrusion depth
    extrusion_color = (0, 0, 0, 255) # Deep black for the 3D block
    space_w = draw.textbbox((0,0), " ", font=font)[2] if font else 15
    
    for line in lines:
        if not line:
            h = font.size if font else 40
            y_offset += h + 20
            continue
            
        line_text = " ".join([w[0] for w in line])
        bbox = draw.textbbox((0, 0), line_text, font=font)
        h = bbox[3] - bbox[1]
        x_offset = 0
        
        for w_text, idx in line:
            c = highlight_color if idx == highlight_idx else fill
            
            # Draw 3D Extrusion
            for i in range(depth, 0, -1):
                draw.text((x_offset + i, y_offset + i), w_text, font=font, fill=extrusion_color)
            
            # Draw main text
            draw.text((x_offset, y_offset), w_text, font=font, fill=c)
            
            w_w = draw.textbbox((0,0), w_text, font=font)[2]
            x_offset += w_w + space_w
            
        y_offset += h + 20 # slightly more line spacing for 3D text
    return y_offset

def generate_text_image(text, width=900, max_height=1600, is_title=False, center=False, highlight_idx=-1):
    """Generates a PIL Image with transparent background containing the text, auto-scaling font to fit max_height."""
    img = Image.new('RGBA', (width, max_height * 2), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    font_size = 90 if is_title else 55
    y_used = 0
    font = None
    
    while font_size > 20:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()
            break 
            
        y_used = draw_text_with_word_wrap(ImageDraw.Draw(Image.new('RGBA', (10,10))), text, width, font)
        if y_used <= max_height:
            break
        font_size -= 2 
    
    y_used = draw_text_with_word_wrap(draw, text, width, font, highlight_idx=highlight_idx)
    
    if y_used > 0:
        img = img.crop((0, 0, width, y_used))
        
    if center and y_used > 0:
        # Create a full-height image and center the text vertically
        final_img = Image.new('RGBA', (width, max_height), (255, 255, 255, 0))
        y_pos = (max_height - y_used) // 2
        final_img.paste(img, (0, y_pos))
        return final_img
        
    return img

async def generate_audio(text, output_file):
    """Generates an MP3 using edge-tts and extracts word timings."""
    voice = "en-US-ChristopherNeural"
    communicate = edge_tts.Communicate(text, voice)
    
    timings = []
    with open(output_file, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start_time = chunk["offset"] / 10**7
                end_time = (chunk["offset"] + chunk["duration"]) / 10**7
                timings.append((chunk["text"], start_time, end_time))
                
    return output_file, timings

def estimate_timings(text, duration):
    """Estimates word timings based on character length and punctuation pauses if edge-tts fails to provide them."""
    words_list = []
    paragraphs = text.split('\n')
    for paragraph in paragraphs:
        if not paragraph.strip(): continue
        for w in paragraph.split(' '):
            if w: words_list.append(w)
            
    weights = []
    for w in words_list:
        weight = len(w)
        if w.endswith('.') or w.endswith(',') or w.endswith(':') or w.endswith('?'):
            weight += 6  # Add extra weight for punctuation pause
        weights.append(weight)
        
    total_weight = sum(weights) if sum(weights) > 0 else 1
    timings = []
    current_time = 0.0
    for i, w in enumerate(words_list):
        word_duration = (weights[i] / total_weight) * duration
        timings.append((w, current_time, current_time + word_duration))
        current_time += word_duration
    return timings

async def generate_synced_audio(text, temp_dir, base_name):
    """Generates audio chunk-by-chunk for perfect timing synchronization."""
    from moviepy import AudioFileClip, concatenate_audioclips
    import re
    
    paragraphs = text.split('\n')
    tasks = []
    valid_chunks = []
    chunk_index = 0
    
    for p in paragraphs:
        if not p.strip(): 
            continue
        # Split paragraph into smaller subchunks by punctuation for micro-estimation
        subchunks = re.split(r'(?<=[.!?,;:]) +', p.strip())
        for sc in subchunks:
            sc_clean = sc.strip()
            if not sc_clean: continue
            valid_chunks.append(sc_clean)
            file_path = os.path.join(temp_dir, f"{base_name}_chunk_{chunk_index}.mp3")
            tasks.append(generate_audio(sc_clean, file_path))
            chunk_index += 1
        
    results = await asyncio.gather(*tasks)
    
    audio_clips = []
    timings = []
    current_time = 0.0
    temp_files = []
    
    for i, (file_path, _) in enumerate(results):
        temp_files.append(file_path)
        clip = AudioFileClip(file_path)
        audio_clips.append(clip)
        
        chunk_text = valid_chunks[i]
        chunk_timings = estimate_timings(chunk_text, clip.duration)
        # Shift chunk timings by current accumulated time
        for w, start, end in chunk_timings:
            timings.append((w, start + current_time, end + current_time))
            
        current_time += clip.duration
        
    final_audio = concatenate_audioclips(audio_clips)
    return final_audio, timings, temp_files

async def create_tiktok_video(question, options, correct_index, explanation, output_path):
    """Generates the full TikTok video."""
    try:
         from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, VideoClip
    except ImportError as e:
         logger.error(f"MoviePy import error: {e}. Please ensure it is installed.")
         return False

    temp_dir = "temp_video_files"
    os.makedirs(temp_dir, exist_ok=True)
    temp_files = []

    try:
        import re
        def clean_option(opt):
            # Remove any leading 'A.', 'A)', '1.', '1)', etc. from the database option
            return re.sub(r'^([A-D][\.\)]\s*|[1-4][\.\)]\s*)', '', opt.strip(), flags=re.IGNORECASE)

        clean_options = [clean_option(opt) for opt in options]
        options_text = "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(clean_options)])
        scene1_text = f"Diagnostic Scenario:\n\n{question}\n\nOptions:\n{options_text}"
        
        correct_answer = clean_options[correct_index]
        scene2_text = f"Correct Answer: {chr(65+correct_index)}\n{correct_answer}\n\nExplanation:\n{explanation}"
        
        scene3_text = " Like and Follow \nFor more medical quizzes!"

        audio1, timings1, tfiles1 = await generate_synced_audio(scene1_text, temp_dir, f"{uuid.uuid4()}_s1")
        audio2, timings2, tfiles2 = await generate_synced_audio(scene2_text, temp_dir, f"{uuid.uuid4()}_s2")
        audio3, timings3, tfiles3 = await generate_synced_audio(scene3_text, temp_dir, f"{uuid.uuid4()}_s3")
        temp_files.extend(tfiles1)
        temp_files.extend(tfiles2)
        temp_files.extend(tfiles3)

        bg_width, bg_height = 1080, 1920
        # More vibrant teal-dark blue gradient (Spotlight center, dark edges)
        bg_pil = create_3d_background(bg_width, bg_height, (40, 100, 130), (5, 15, 35))
        bg_np = np.array(bg_pil)

        def get_active_word_idx(timings, t):
            # Find the word index that matches the current time
            for i, (word, start, end) in enumerate(timings):
                if start <= t <= end:
                    return i
            return -1

        # Caching text images to drastically improve render speed
        scene1_cache = {}
        def make_frame_scene1(t):
            if t > audio1.duration:
                idx = -1
            else:
                idx = get_active_word_idx(timings1, t)
            
            if idx not in scene1_cache:
                img_pil = generate_text_image(scene1_text, width=950, center=True, highlight_idx=idx)
                scene1_cache[idx] = np.array(img_pil)
            return scene1_cache[idx]
            
        scene2_cache = {}
        def make_frame_scene2(t):
            if t > audio2.duration:
                idx = -1
            else:
                idx = get_active_word_idx(timings2, t)
                
            if idx not in scene2_cache:
                img_pil = generate_text_image(scene2_text, width=950, center=True, highlight_idx=idx)
                scene2_cache[idx] = np.array(img_pil)
            return scene2_cache[idx]
            
        scene3_cache = {}
        def make_frame_scene3(t):
            if t > audio3.duration:
                idx = -1
            else:
                idx = get_active_word_idx(timings3, t)
                
            if idx not in scene3_cache:
                img_pil = generate_text_image(scene3_text, width=950, center=True, highlight_idx=idx)
                scene3_cache[idx] = np.array(img_pil)
            return scene3_cache[idx]

        bg_clip1 = ImageClip(bg_np).with_duration(audio1.duration + 5.0) 
        text_clip1 = VideoClip(make_frame_scene1, duration=audio1.duration + 5.0).with_position('center')
        
        # Countdown Timer generation
        timer_clips = []
        for i in range(5, 0, -1):
            timer_img = generate_text_image(str(i), width=200, max_height=200, is_title=True)
            t_clip = ImageClip(np.array(timer_img)).with_position(('center', 1600)).with_start(audio1.duration + (5-i)).with_duration(1.0)
            timer_clips.append(t_clip)

        scene1 = CompositeVideoClip([bg_clip1, text_clip1] + timer_clips).with_audio(audio1)

        bg_clip2 = ImageClip(bg_np).with_duration(audio2.duration + 1.5)
        text_clip2 = VideoClip(make_frame_scene2, duration=bg_clip2.duration).with_position('center')
        scene2 = CompositeVideoClip([bg_clip2, text_clip2]).with_audio(audio2)
        
        bg_clip3 = ImageClip(bg_np).with_duration(audio3.duration + 2.0)
        text_clip3 = VideoClip(make_frame_scene3, duration=bg_clip3.duration).with_position('center')
        scene3 = CompositeVideoClip([bg_clip3, text_clip3]).with_audio(audio3)

        final_video = concatenate_videoclips([scene1, scene2, scene3])
        
        logger.info(f"Writing final video to {output_path}...")
        
        # Write file in thread to avoid blocking asyncio loop
        def write_video():
            final_video.write_videofile(
                output_path, 
                fps=24, 
                codec="libx264", 
                audio_codec="aac",
                preset="ultrafast", # Faster rendering
                logger=None # Suppress verbose progress bar
            )
        
        await asyncio.to_thread(write_video)
        
        # Close clips to free memory
        audio1.close()
        audio2.close()
        audio3.close()
        scene1.close()
        scene2.close()
        scene3.close()
        final_video.close()

        logger.info(f"Successfully generated video at {output_path}")
        return True

    except Exception as e:
        logger.error(f"Error generating video: {e}", exc_info=True)
        return False
    finally:
        # Cleanup temporary audio files
        for f in temp_files:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except Exception as cleanup_err:
                    logger.warning(f"Failed to remove temp file {f}: {cleanup_err}")

# Async Wrapper to ensure zero impact on main bot
async def background_video_task(question, options, correct_index, explanation):
    """Wrapper to be called via asyncio.create_task"""
    try:
        from tiktok_poster import post_video_to_tiktok
        
        videos_dir = "tiktok_videos"
        os.makedirs(videos_dir, exist_ok=True)
        
        # Make a safe filename based on question (first 20 chars)
        safe_q = "".join([c for c in question[:20] if c.isalpha() or c.isdigit()]).rstrip()
        filename = f"{videos_dir}/{safe_q}_{uuid.uuid4().hex[:6]}.mp4"
        
        logger.info(f"▶️ Starting background video generation task for: {filename}")
        success = await create_tiktok_video(question, options, correct_index, explanation, filename)
        
        if success and os.path.exists(filename):
            logger.info(f"✅ Video created successfully: {filename}")
            logger.info(f"⏳ Starting upload to TikTok for: {filename}")
            
            posted = await post_video_to_tiktok(filename)
            
            if posted:
                logger.info(f"🚀 Successful upload to TikTok for: {filename}")
                try:
                    os.remove(filename)
                    logger.info(f"🗑️ Deleted video file from computer permanently: {filename}")
                except Exception as del_err:
                    logger.error(f"⚠️ Failed to delete video file {filename}: {del_err}")
            else:
                logger.warning(f"❌ Failed upload to TikTok for: {filename}. Video was kept on disk for manual review.")
        else:
            logger.warning(f"⚠️ Video generation failed — skipping TikTok upload.")
            
        logger.info(f"Finished background video task.")
    except Exception as e:
        logger.error(f"Background video task failed critically: {e}", exc_info=True)

if __name__ == "__main__":
    # Test execution
    test_q = "A 65-year-old male presents with acute shortness of breath and chest pain. ECG shows ST elevation in V1-V4."
    test_opts = ["Administer Aspirin", "Perform PCI", "Give Nitroglycerin", "Give Beta Blockers"]
    test_idx = 1
    test_exp = "The patient is experiencing an anteroseptal myocardial infarction. PCI is the definitive treatment to restore blood flow."
    
    asyncio.run(background_video_task(test_q, test_opts, test_idx, test_exp))
