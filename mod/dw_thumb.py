from moviepy.editor import VideoFileClip
from PIL import Image
import requests
import os
import re

def download_thumbnail(video_id, video_path, thumbnail_path):
    thumbnail_path = os.path.join(os.path.dirname(video_path), 'thumbnail.jpg')
    # Try downloading thumbnail directly from YouTube
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
    response = requests.get(thumbnail_url)
    if response.status_code == 200:
        with open(thumbnail_path, 'wb') as f:
            f.write(response.content)
        return thumbnail_path
    else:
        print(f'Failed to download thumbnail from YouTube for video ID: {video_id}')
        try:
            clip = VideoFileClip(video_path)
            duration = clip.duration
            thumbnail_time = duration / 2
            frame = clip.get_frame(thumbnail_time)
            image = Image.fromarray(frame)
            image.save(thumbnail_path)
            clip.close()
            return thumbnail_path
        except Exception as e:
            print(f'Failed to generate thumbnail using MoviePy: {e}')
            return None

def extract_video_id(video_link):
    pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.match(pattern, video_link)
    if match:
        return match.group(1)
    else:
        return None