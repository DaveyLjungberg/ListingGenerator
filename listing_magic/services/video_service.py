"""
Video Service

Handles all video generation functionality including basic video creation
and voiceover generation using gTTS.
"""

import os
import re
import numpy as np
from moviepy import ImageClip, CompositeVideoClip, AudioFileClip, vfx
from gtts import gTTS

# Import from our utils
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.image_processor import resize_with_padding


def generate_video(images, file_manager):
    """
    Generate a property tour video from images

    Args:
        images: List of PIL Image objects
        file_manager: FileManager instance for temp file handling

    Returns:
        str: Path to the generated video file
    """
    clips = []
    for i, img in enumerate(images):
        # Images are already EXIF-transposed from cache

        # Resize with padding (Letterboxing)
        img = resize_with_padding(img, (1920, 1080))

        # Convert PIL Image to numpy array
        img_array = np.array(img.convert('RGB'))

        # Create ImageClip
        clip = ImageClip(img_array).with_duration(3)

        # Apply crossfade and positioning
        if i > 0:
            start_time = i * 2  # 3s duration - 1s overlap
            clip = clip.with_start(start_time).with_effects([vfx.CrossFadeIn(1)])

        clips.append(clip)

    # Create composite video
    video = CompositeVideoClip(clips)
    output_path = file_manager.get_path("property_tour.mp4")

    # Write video file
    video.write_videofile(output_path, fps=24, codec='libx264', preset='ultrafast')

    # Close video resource
    video.close()

    return output_path


def extract_narration_from_script(script_text):
    """
    Extract only the spoken narration from a formatted video script.
    Removes timestamps, scene labels, and formatting - keeps only quoted narration.

    Args:
        script_text: Full video script with formatting

    Returns:
        Clean narration text ready for TTS
    """

    # Method 1: Extract text within double quotes (most reliable)
    # Finds all text between " and " characters
    quoted_text = re.findall(r'"([^"]*)"', script_text)

    if quoted_text:
        # Join all quoted sections with a space
        narration = ' '.join(quoted_text)

        # Clean up any extra spaces
        narration = re.sub(r'\s+', ' ', narration).strip()

        return narration

    # Method 2: If no quotes found, try to extract after "Audio (Voiceover):"
    voiceover_pattern = r'\*\*Audio \(Voiceover\):\*\*\s*(.+?)(?=\*\*\d|$)'
    voiceover_matches = re.findall(voiceover_pattern, script_text, re.DOTALL)

    if voiceover_matches:
        # Clean each match
        clean_matches = []
        for match in voiceover_matches:
            # Remove any remaining markdown
            clean = re.sub(r'\*\*', '', match)
            # Remove quotes if present
            clean = clean.strip().strip('"\'')
            clean_matches.append(clean)

        narration = ' '.join(clean_matches)
        narration = re.sub(r'\s+', ' ', narration).strip()
        return narration

    # Method 3: Last resort - try to remove obvious formatting
    lines = script_text.split('\n')
    clean_lines = []

    for line in lines:
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Skip lines that start with timestamp formatting
        if re.match(r'^\*\*\d+:\d+', line):
            continue

        # Skip lines that are just Visual labels
        if re.match(r'^\*\*Visual:', line, re.IGNORECASE):
            continue

        # Skip scene headers
        if re.match(r'^Scene \d+:', line, re.IGNORECASE):
            continue

        # If we got here, might be narration
        # Remove markdown bold
        line = re.sub(r'\*\*', '', line)

        if line:
            clean_lines.append(line)

    narration = ' '.join(clean_lines)
    narration = re.sub(r'\s+', ' ', narration).strip()

    return narration


def generate_video_with_voiceover(images, script_text, file_manager):
    """
    Generate property tour video with AI voiceover

    Args:
        images: List of PIL Image objects
        script_text: Video script text containing narration
        file_manager: FileManager instance for temp file handling

    Returns:
        str: Path to the generated video file with voiceover
    """

    # CRITICAL: Clean the script to extract only narration
    clean_narration = extract_narration_from_script(script_text)

    # Validate we have narration to speak
    if not clean_narration or len(clean_narration.strip()) < 10:
        raise ValueError("Could not extract narration from script. Please check script format.")

    # Debug: Show what will be spoken
    print(f"DEBUG - Original script length: {len(script_text)} chars")
    print(f"DEBUG - Clean narration length: {len(clean_narration)} chars")
    print(f"DEBUG - Narration to speak: {clean_narration[:200]}...")  # First 200 chars

    # Generate voiceover audio from cleaned narration
    tts = gTTS(text=clean_narration, lang='en', slow=False)
    audio_path = file_manager.get_path("voiceover.mp3")
    tts.save(audio_path)

    # Load audio
    audio = AudioFileClip(audio_path)
    audio_duration = audio.duration

    # Calculate image duration based on audio length
    duration_per_image = audio_duration / len(images)

    # Create video clips
    clips = []
    for i, img in enumerate(images):
        # Images are already EXIF-transposed from cache
        img = resize_with_padding(img, (1920, 1080))
        img_array = np.array(img.convert('RGB'))

        clip = ImageClip(img_array).with_duration(duration_per_image)

        # Add crossfade transitions
        if i > 0:
            overlap = min(0.5, duration_per_image * 0.2)  # 20% overlap or 0.5s max
            start_time = i * (duration_per_image - overlap)
            clip = clip.with_start(start_time).with_effects([vfx.CrossFadeIn(overlap)])

        clips.append(clip)

    # Create composite video
    video = CompositeVideoClip(clips)

    # Add audio to video
    final_video = video.with_audio(audio)

    output_path = file_manager.get_path("property_tour_with_voice.mp4")
    final_video.write_videofile(output_path, fps=24, codec='libx264', preset='ultrafast', audio_codec='aac')

    # Cleanup: Close resources first, then remove temporary files
    audio.close()
    video.close()

    # Remove temporary audio file after resources are closed
    if os.path.exists(audio_path):
        os.remove(audio_path)

    return output_path
