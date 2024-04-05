from moviepy.editor import VideoFileClip
import os

def get_video_info(video_path):
    try:
        clip = VideoFileClip(video_path)
        duration = clip.duration
        width, height = clip.size
        clip.close()
        print("Video information retrieved successfully!")
        return duration, width, height
    except Exception as e:
        print(f"Error getting video info: {e}")
        return None, None, None
