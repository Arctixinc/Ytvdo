from pyrogram import Client, filters
from pytube import YouTube
import requests
import os
import asyncio
from moviepy.editor import VideoFileClip

# Replace 'YOUR_API_ID', 'YOUR_API_HASH', and 'YOUR_BOT_TOKEN' with your actual values
API_ID = '25033101'
API_HASH = 'd983e07db3fe330a1fd134e61604e11d'
BOT_TOKEN = '6285135839:AAE5savazJeNxwkAnGW3mW9l-4hUPLLoUds'

# Create a Pyrogram client
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Start command handler
@app.on_message(filters.command("start"))
async def start(client, message):
    user = message.from_user
    await message.reply_text(f"Hello, @{user.username}!\n\nSend me the YouTube link of the video you want to upload.")

# Help command handler
@app.on_message(filters.command("help"))
async def help(client, message):
    help_text = """
    Welcome to the YouTube Video Uploader Bot!

To upload a YouTube video, simply send me the YouTube link.
    
Enjoy using the bot!

   ©️ Channel : @NT_BOT_CHANNEL
    """
    await message.reply_text(help_text)

# Message handler for processing YouTube links
@app.on_message(filters.regex(r'^(http(s)?:\/\/)?((w){3}.)?youtu(be|.be)?(\.com)?\/.+'))
async def process_youtube_link(client, message):
    youtube_link = message.text
    try:
        # Downloading text message
        downloading_msg = await message.reply_text("Downloading video...")

        # Download the YouTube video
        yt = YouTube(youtube_link)
        video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        #video = yt.streams.filter(progressive=True, file_extension='mp4').first()
        video.download(filename='downloaded_video.mp4')

        # Download the thumbnail
        thumbnail_url = yt.thumbnail_url
        thumbnail_response = requests.get(thumbnail_url)
        with open('thumbnail.jpg', 'wb') as f:
            f.write(thumbnail_response.content)

        # Get video duration, height, and width using moviepy
        clip = VideoFileClip('downloaded_video.mp4')
        duration = int(clip.duration)
        height = int(clip.size[1])
        width = int(clip.size[0])
        clip.close()

        # Uploading text message
        uploading_msg = await message.reply_text("Uploading video...")

        # Send the video file to the user with the thumbnail as caption
        sent_message = await app.send_video(
            message.chat.id, 
            video=open('downloaded_video.mp4', 'rb'), 
            caption=yt.title,
            duration=duration,
            height=height,
            width=width,
            thumb=open('thumbnail.jpg', 'rb')
        )

        # Delay for a few seconds and delete downloading and uploading
        await downloading_msg.delete()
        await uploading_msg.delete()
        await asyncio.sleep(2)

        # Delete downloading and uploading text messages
        await app.delete_messages(message.chat.id, [downloading_msg.message_id, uploading_msg.message_id])

        # Delete the downloaded video and thumbnail files
        os.remove('downloaded_video.mp4')
        os.remove('thumbnail.jpg')

    except Exception as e:
        error_text = 'OWNER : @LISA_FAN_LK 💕\nFor the List of Telegram Bots'
        await message.reply_text(error_text)

# Start the bot
print("🎊 I AM ALIVE 🎊")
app.run()
    
