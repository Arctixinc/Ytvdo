import os
from Arctix import Arctix as app
from pyrogram import Client

async def send_screenshots(chat_id, screenshot_directory, progress=None):
    for i in range(10):  # Iterate from 0 to 9
        screenshot_file = f"screenshot_{i}.jpg"
        screenshot_path = os.path.join(screenshot_directory, screenshot_file)

        if os.path.exists(screenshot_path):  # Check if the screenshot file exists
            await app.send_photo(chat_id, photo=screenshot_path, progress=progress)
            os.remove(screenshot_path)
            