from moviepy.editor import VideoFileClip
from PIL import Image
import os

def create_screenshot(video_path, output_folder):
    try:
        clip = VideoFileClip(video_path)
        duration = clip.duration
        clip.close()

        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)

        # Capture screenshots
        num_screenshots = 10
        interval = duration / num_screenshots
        for i in range(num_screenshots):
            time_point = i * interval
            clip = VideoFileClip(video_path)
            frame = clip.get_frame(time_point)
            image = Image.fromarray(frame)
            screenshot_path = os.path.join(output_folder, f'screenshot_{i}.jpg')
            image.save(screenshot_path)
            clip.close()
            print(f"Screenshot {i} created: {screenshot_path}")

        print("Screenshots created successfully!")
    except Exception as e:
        print(f"Error creating screenshots: {e}")
