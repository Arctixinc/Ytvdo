import os
import re

def progress(current, total):
    progress_percent = current * 100 / total
    bar_length = 20
    num_filled_blocks = int(bar_length * progress_percent / 100)
    progress_bar = f"[{'█' * num_filled_blocks}{'-' * (bar_length - num_filled_blocks)}] {progress_percent:.1f}%"
    print(progress_bar, end='\r')
