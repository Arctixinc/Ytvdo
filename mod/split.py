import subprocess
import os
import math

def split_video(input_video, folder_path, first_chunk_size_mb=2088):
    try:
        # Get total size of the input video
        input_size_mb = os.path.getsize(input_video) / (1024 * 1024)

        # Calculate the number of full-sized chunks and the size of each remaining chunk
        num_full_chunks = math.floor(input_size_mb / first_chunk_size_mb)
        remaining_size_mb = input_size_mb - (num_full_chunks * first_chunk_size_mb)
        num_remaining_chunks = num_full_chunks + (1 if remaining_size_mb > 0 else 0)
        remaining_chunk_size_mb = math.ceil(remaining_size_mb / (num_remaining_chunks - 1)) if num_remaining_chunks > 1 else 0

        # Split the video into chunks
        input_filename, input_extension = os.path.splitext(input_video)
        start_time = 0
        for i in range(num_full_chunks):
            output_file = os.path.join(folder_path, f"{input_filename}_part_{i + 1:03d}{input_extension}")
            split_cmd = [
                "ffmpeg", "-i", input_video, "-ss", str(start_time), "-fs", f"{first_chunk_size_mb}M",
                "-c:v", "copy", "-c:a", "copy", output_file
            ]
            subprocess.run(split_cmd, check=True)  # Added check=True for error checking
            print(f"Chunk {i + 1}/{num_full_chunks} created.")
            start_time += first_chunk_size_mb

        if num_remaining_chunks > 0:
            output_file = os.path.join(folder_path, f"{input_filename}_part_{num_full_chunks + 1:03d}{input_extension}")
            split_cmd = [
                "ffmpeg", "-i", input_video, "-ss", str(start_time), "-fs", f"{remaining_chunk_size_mb}M",
                "-c:v", "copy", "-c:a", "copy", output_file
            ]
            subprocess.run(split_cmd, check=True)  # Added check=True for error checking
            print(f"Chunk {num_full_chunks + 1}/{num_full_chunks + 1} created.")

        # Delete the original video file
        os.remove(input_video)
        print("Original video deleted after successful splitting.")
    except subprocess.CalledProcessError as e:
        print(f"Error splitting video: {e}")
    except Exception as e:
        print(f"Error splitting video and deleting original: {e}")
