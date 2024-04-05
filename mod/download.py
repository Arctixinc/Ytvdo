import os
import subprocess

def download_video(url, folder_path):
    output_format = os.path.join(folder_path, '%(title)s.%(ext)s')
    command = [
        'yt-dlp',
        '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
        '-o', output_format,
        '--external-downloader', 'aria2c',  # Specify aria2c as the external downloader
        '--external-downloader-args', '-x 16',  # Add arguments for aria2c (optional)
        url
    ]
    
    # Execute the command
    try:
        subprocess.run(command, check=True)
        video_title = subprocess.check_output(['yt-dlp', '--get-filename', '-o', '%(title)s', url], universal_newlines=True).strip()
        video_path = os.path.join(folder_path, f"{video_title}.mp4")        
        return video_path
    except subprocess.CalledProcessError as e:
        print(f"Error downloading video: {e}")
        return None
