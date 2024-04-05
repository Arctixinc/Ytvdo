from pyrogram.errors import PeerIdInvalid
from pyrogram import Client
app = Client("my_account", bot_token="6732118607:AAEljUlpetKGaxwxb_8nV4VPOgx1BR9pZXU", api_id="11405252", api_hash="b1a1fc3dc52ccc91781f33522255a880")   

def send_telegram_video(user_id, video_path, thumbnail_path, caption, duration, width, height, supports_streaming, progress):
    try:
        app.send_video(
            user_id,
            video=video_path,
            caption=caption,
            duration=duration,
            width=width,
            height=height,
            thumb=thumbnail_path,         
            supports_streaming=True,
            progress=progress 
        )
        print(f'Video "{video_path}" sent successfully!')
    except PeerIdInvalid as e:
        print(f'Telegram says: [{e.CODE}] - {e.MESSAGE}')
        print(f'Make sure your bot is allowed to message the user with ID {user_id}')
    except Exception as e:
        print(f'Error sending video "{video_path}": {e}')

def send_telegram_screenshot(user_id, screenshot_path, progress):
    try:
        # Send the screenshot to the user
        app.send_photo(user_id, photo=screenshot_path, progress=progress)
        print(f'Screenshot sent successfully!')
    except PeerIdInvalid as e:
        print(f'Telegram says: [{e.CODE}] - {e.MESSAGE}')
        print(f'Make sure your bot is allowed to message the user with ID {user_id}')
    except Exception as e:
        print(f'Error sending screenshot: {e}')
