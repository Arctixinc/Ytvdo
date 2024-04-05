from pyrogram import Client, filters
from pytube import YouTube
import requests
import os
import asyncio
import random
import shutil
from moviepy.editor import VideoFileClip
from mod.progress import progress
from mod.download import download_video
from mod.split import split_video
from mod.dw_thumb import extract_video_id, download_thumbnail
from mod.video_info import get_video_info
from mod.screenshort import create_screenshot
from mod.send_video import send_video
from mod.send_screenshot import send_screenshots
from pyrogram.types import Message
from requests import Session
from urllib.parse import urlparse, parse_qs
from os import path
from http.cookiejar import MozillaCookieJar
from re import findall

# Replace 'YOUR_API_ID', 'YOUR_API_HASH', and 'YOUR_BOT_TOKEN' with your actual values
API_ID = '16625410'
API_HASH = '510fc67d35935ca8d2e1eac4a09d83db'
BOT_TOKEN = '5847447231:AAEg6CpQdP1dVATizrT8EzwRrSzFj6tYba4'

download_folder = "download"
screenshot_directory = "screenshots"
SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']


# Create a Pyrogram client
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

class DirectDownloadLinkException(Exception):
    pass
    
def get_readable_file_size(size_in_bytes):
    if size_in_bytes is None:
        return '0B'
    index = 0
    while size_in_bytes >= 1024 and index < len(SIZE_UNITS) - 1:
        size_in_bytes /= 1024
        index += 1
    return f'{size_in_bytes:.2f}{SIZE_UNITS[index]}' if index > 0 else f'{size_in_bytes}B'    

def terabox(url):
    if not path.isfile('cookies.txt'):
        raise DirectDownloadLinkException("cookies.txt not found")
    try:
        jar = MozillaCookieJar('cookies.txt')
        jar.load()
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    cookies = {}
    for cookie in jar:
        cookies[cookie.name] = cookie.value
    details = {'contents':[], 'title': '', 'total_size': 0}
    details["header"] = ' '.join(f'{key}: {value}' for key, value in cookies.items())

    def __fetch_links(session, dir_='', folderPath=''):
        params = {
            'app_id': '250528',
            'jsToken': jsToken,
            'shorturl': shortUrl
            }
        if dir_:
            params['dir'] = dir_
        else:
            params['root'] = '1'
        try:
            _json = session.get("https://www.1024tera.com/share/list", params=params, cookies=cookies).json()
        except Exception as e:
            raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
        if _json['errno'] not in [0, '0']:
            if 'errmsg' in _json:
                raise DirectDownloadLinkException(f"ERROR: {_json['errmsg']}")
            else:
                raise DirectDownloadLinkException('ERROR: Something went wrong!')

        if "list" not in _json:
            return
        contents = _json["list"]
        for content in contents:
            if content['isdir'] in ['1', 1]:
                if not folderPath:
                    if not details['title']:
                        details['title'] = content['server_filename']
                        newFolderPath = path.join(details['title'])
                    else:
                        newFolderPath = path.join(details['title'], content['server_filename'])
                else:
                    newFolderPath = path.join(folderPath, content['server_filename'])
                __fetch_links(session, content['path'], newFolderPath)
            else:
                if not folderPath:
                    if not details['title']:
                        details['title'] = content['server_filename']
                    folderPath = details['title']
                item = {
                    'url': content['dlink'],
                    'filename': content['server_filename'],
                    'path' : path.join(folderPath),
                }
                if 'size' in content:
                    size = content["size"]
                    if isinstance(size, str) and size.isdigit():
                        size = float(size)
                    details['total_size'] += size
                details['contents'].append(item)
    with Session() as session:
        try:
            _res = session.get(url, cookies=cookies)
        except Exception as e:
            raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
        if jsToken := findall(r'window\.jsToken.*%22(.*)%22', _res.text):
            jsToken = jsToken[0]
        else:
            raise DirectDownloadLinkException('ERROR: jsToken not found!.')
        shortUrl = parse_qs(urlparse(_res.url).query).get('surl')
        if not shortUrl:
            raise DirectDownloadLinkException("ERROR: Could not find surl")
        try:
            __fetch_links(session)
        except Exception as e:
            raise DirectDownloadLinkException(e)

    # Modify the link
    details['contents'][0]['url'] = details['contents'][0]['url'].replace("d.1024tera.com", "d3.terabox.app").replace("&reg", "%26reg")

    

    file_name = f"[{details['title']}]({url})"
    file_size = get_readable_file_size(details['total_size'])
    return f"┎ **Title:** {file_name}\n┠ **Size:** `{file_size}`\n┖ **Link:** [Link]({details['contents'][0]['url']})"


# Terabox link processing handler
@app.on_message(filters.command(["terabox"]))
async def terabox_command_handler(_, message: Message):
    # Extract the link from the command
    command_parts = message.text.split(" ", 1)
    if len(command_parts) < 2:
        await app.send_message(message.chat.id, "Please provide the Terabox link.")
        return
    
    url = command_parts[1]

    try:
        result = terabox(url)
        await app.send_message(message.chat.id, result)
    except DirectDownloadLinkException as e:
        await app.send_message(message.chat.id, f"An error occurred: {e}")
        #LOGGER.error(f"Terabox link processing error: {e}")

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
        
@app.on_message(filters.command("vdw") & filters.regex(r'https?://\S+'))
async def process_url(_, update):    
    video_url = update.text.split()[-1]
    
    # Generate a random number to use as the folder name
    folder_name = str(random.randint(1000, 9999))
    message_folder_path = os.path.join(download_folder, folder_name)
    os.makedirs(message_folder_path, exist_ok=True)
    #LOGGER.info("Folder created: %s", message_folder_path)
    
    await app.send_message(update.chat.id, f"Your download has started. here is the link {video_url}")
    #LOGGER.info("Download started for video URL: %s", video_url)
    
    try:
        video_path = download_video(video_url, message_folder_path)
        if not video_path:
            raise Exception("Download failed")
        
        print("Checking video size...")
        # Check video size
        video_size_mb = os.path.getsize(video_path) / (1024 * 1024)  # Convert bytes to MB
        if video_size_mb > 2000:
            print("Video size is more than 2000MB. Splitting the video...")
            #LOGGER.info("Video size is more than 2000MB. Splitting the video...")
            split_video(video_path, message_folder_path)
            print("Video split successfully. Removing original video...")
        
        await app.send_message(update.chat.id, "Your download was completed")  
        
        video_files = [file for file in os.listdir(message_folder_path) if file.endswith(".mp4")]
        video_files.sort()
        
        for video_file in video_files:
            videos_path = os.path.join(message_folder_path, video_file)
            video_filename = os.path.splitext(video_file)[0]
            
            video_id = extract_video_id(video_url)
            thumbnail_path = download_thumbnail(video_id, videos_path, os.path.join(message_folder_path, 'thumbnail.jpg'))
            
            if thumbnail_path:
                duration, width, height = get_video_info(videos_path)
                
                if duration is not None and width is not None and height is not None:
                    await app.send_message(update.chat.id, "Screenshot creation has started.....")
                    #LOGGER.info("Screenshot creation started for video: %s", videos_path)
                    create_screenshot(videos_path, os.path.join(screenshot_directory, folder_name))
                    await app.send_message(update.chat.id, "Screenshot Created Successfully....")
                    #LOGGER.info("Screenshot created successfully for video: %s", videos_path)
                    
                    await app.send_message(update.chat.id, "Video Uploading....")
                    
                    await send_video(
                        update.chat.id, 
                        videos_path, 
                        thumbnail_path, 
                        duration, 
                        width, 
                        height, 
                        caption=video_filename, 
                        progress=progress
                    )
                    
                    await send_screenshots(update.chat.id, os.path.join(screenshot_directory, folder_name))
                            
                    os.remove(videos_path)     
                    await app.send_message(update.chat.id, "Video and screenshots sent successfully.")
                    # Delete the created folders after sending the video and screenshots
                    shutil.rmtree(os.path.join(download_folder, folder_name))
                    shutil.rmtree(os.path.join(screenshot_directory, folder_name))
                    #LOGGER.info("Folders deleted: %s, %s", os.path.join(download_folder, folder_name), os.path.join(screenshot_directory, folder_name))
                        
                else:
                    await app.send_message(update.chat.id, "Failed to get video information.")
                    #LOGGER.error("Failed to get video information for video: %s", videos_path)
            else:
                await app.send_message(update.chat.id, "Failed to download the video thumbnail.")
                #LOGGER.error("Failed to download thumbnail for video: %s", videos_path)

    except Exception as e:
        await app.send_message(update.chat.id, "Failed to download the video.")
        #LOGGER.error("Failed to download video from URL: %s", video_url)
        shutil.rmtree(message_folder_path)  # Remove the folder in case of download failure

# Start the bot
print("🎊 I AM ALIVE 🎊")
app.run()
    
