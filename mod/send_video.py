from pyrogram import Client
from Arctix import Arctix as app

async def send_video(chat_id, video_path, thumbnail_path, duration, width, height, caption, progress=None):
    await app.send_video(
        chat_id,
        video=video_path,
        caption=caption,
        duration=int(duration),
        width=width,
        height=height,
        thumb=thumbnail_path,
        supports_streaming=True,
        progress=progress
    )
    