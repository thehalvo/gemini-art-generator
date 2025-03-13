"""
NOTE:
python3 -m venv venv

source venv/bin/activate

pip install Pillow google-genai loguru

python generate.py
"""

from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import os
import subprocess
import tempfile
from loguru import logger as log
import uuid
import time

GEMINI_API_KEY = "YOU_KEY_HERE"

client = genai.Client(api_key=GEMINI_API_KEY)

subject = "a seed growing into a plant and then blooming into a flower"
style = "in a 8-bit pixel art style"
template = "Create an animation by generationg multiple frames, showing"

contents = f"{template} {subject} {style}"

def generate_frames(prompt, max_retries=3):
    """Generate animation frames with retry logic if only one frame is returned."""
    for attempt in range(1, max_retries + 1):
        log.info(f"Attempt {attempt}/{max_retries}: Sending request to Gemini with prompt: {prompt}")
        
        response = client.models.generate_content(
            model="models/gemini-2.0-flash-exp",
            contents=prompt,
            config=types.GenerateContentConfig(response_modalities=['Text', 'Image'])
        )
        
        # Count the number of image frames
        frame_count = 0
        if response.candidates:
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    frame_count += 1
        
        log.info(f"Received {frame_count} frames in response")
        
        # If we got multiple frames, return the response
        if frame_count > 1:
            log.info(f"Successfully received {frame_count} frames on attempt {attempt}")
            return response
        
        # If this was the last attempt, return what we have
        if attempt == max_retries:
            log.warning(f"Failed to get multiple frames after {max_retries} attempts. Proceeding with {frame_count} frames.")
            return response
        
        # Otherwise, try again with a stronger prompt
        log.warning(f"Only received {frame_count} frame(s). Retrying with enhanced prompt...")
        prompt = f"{prompt} Please create at least 5 distinct frames showing different stages of the animation."
        time.sleep(1)  # Small delay between retries

# Get response with retry logic
response = generate_frames(contents)

# Create a temporary directory to store the frames
with tempfile.TemporaryDirectory() as temp_dir:
    log.info(f"Created temporary directory at {temp_dir}")
    frame_paths = []
    frame_count = 0
    
    # Process and save each part
    log.info(f"Number of candidates: {len(response.candidates)}")
    if response.candidates:
        log.info(f"Number of parts in first candidate: {len(response.candidates[0].content.parts)}")
        
        for part_index, part in enumerate(response.candidates[0].content.parts):
            if part.text is not None:
                log.info(f"Text content: {part.text[:100]}...")
                print(part.text)
            elif part.inline_data is not None:
                # Save the image to a temporary file
                frame_path = os.path.join(temp_dir, f"frame_{frame_count:03d}.png")
                image = Image.open(BytesIO(part.inline_data.data))
                image.save(frame_path)
                frame_paths.append(frame_path)
                frame_count += 1
            else:
                log.warning(f"Part {part_index+1} has neither text nor inline_data")
    else:
        log.error("No candidates returned in the response")
    
    # If we have frames, create a GIF using ffmpeg
    if frame_paths:
        log.info(f"Found {len(frame_paths)} frames to process")
        output_path = os.path.abspath(f"animation_{uuid.uuid4()}.gif")
        log.info(f"Will save animation to {output_path}")
        
        # List all files in the temp directory to verify
        log.info(f"Files in temp directory: {os.listdir(temp_dir)}")
        
        # Build ffmpeg command
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",  # Overwrite output file if it exists
            "-framerate", "2",  # 2 frames per second
            "-pattern_type", "glob",
            "-i", f"{temp_dir}/frame_*.png",
            "-vf", "scale=512:-1:flags=lanczos",  # Resize while maintaining aspect ratio
            output_path
        ]
        
        try:
            cmd_str = ' '.join(ffmpeg_cmd)
            log.info(f"Running ffmpeg command: {cmd_str}")
            
            # Run ffmpeg and capture output
            result = subprocess.run(
                ffmpeg_cmd, 
                check=True,
                capture_output=True,
                text=True
            )
            
            log.info(f"ffmpeg stdout: {result.stdout}")
            
            if os.path.exists(output_path):
                log.info(f"Animation successfully saved to {output_path}")
                file_size = os.path.getsize(output_path)
                log.info(f"File size: {file_size} bytes")
                
                # Open the resulting GIF
                Image.open(output_path).show()
            else:
                log.error(f"Output file {output_path} was not created")
        except subprocess.CalledProcessError as e:
            log.error(f"Failed to create GIF: {e}")
            log.error(f"ffmpeg stdout: {e.stdout}")
            log.error(f"ffmpeg stderr: {e.stderr}")
        except Exception as e:
            log.error(f"Unexpected error: {str(e)}")
    else:
        log.warning("No frames were generated, cannot create animation")

log.info("Script completed")
