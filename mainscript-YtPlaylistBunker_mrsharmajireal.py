# Youtube Playlist Downloader Script
# Author: Vishal Sharma - @mrsharmajireal + ChatGPT4o
# Contact: mrsharmajireal+ytplaylistbunker@gmail.com
# Date: June 2024
# Description: Your next favourite python script to download videos from YouTube playlists.
# Providing Options - Currently you can only download video in .Mp4 Format with (720P or else 360p)

import os
import re
from pytube import YouTube
import requests

# Helper functions
def sanitize_filename(filename):
    # Remove illegal characters for filenames but keep the file extension intact
    filename = re.sub(r'[^\w\s.-]', '', filename)
    return filename.strip()

def foldertitle(url):
    try:
        res = requests.get(url)
        res.raise_for_status()
    except requests.RequestException as e:
        print(f'Error fetching URL: {e}')
        return False

    if 'list=' in url:
        eq = url.rfind('=') + 1
        cPL = url[eq:]
    else:
        print('Incorrect playlist URL.')
        return False

    return cPL

def link_snatcher(url):
    our_links = []
    try:
        res = requests.get(url)
        res.raise_for_status()
    except requests.RequestException as e:
        print(f'Error fetching URL: {e}')
        return False

    plain_text = res.text

    if 'list=' in url:
        eq = url.rfind('=') + 1
        cPL = url[eq:]
    else:
        print('Incorrect playlist URL.')
        return False

    tmp_mat = re.compile(r'watch\?v=\S+?list=' + cPL)
    mat = re.findall(tmp_mat, plain_text)

    for m in mat:
        new_m = m.replace('&amp;', '&')
        work_m = 'https://youtube.com/' + new_m
        if work_m not in our_links:
            our_links.append(work_m)

    return our_links

# Set base directory to current working directory
BASE_DIR = os.getcwd()

# Print welcome message and script details
print('Welcome to YtPlaylistBunker Created by Vishal Sharma - @mrsharmajireal')
print("""# Title:Youtube Playlist Downloader Script
# Author: Vishal Sharma - @mrsharmajireal + ChatGPT4o
# Contact: mrsharmajireal+ytplaylistbunker@gmail.com
# Date: June 2024
# Description: Your next favourite python script to download videos from YouTube playlists.
# Providing Options - Currently you can only download video in .Mp4 Format with (720P or else 360p)""")

# Prompt user for playlist URL and desired resolution
url = input("\nSpecify your playlist URL: ").strip()

print('\nCHOOSE ANY ONE - TYPE 360P OR 720P\n')
user_res = input().strip().lower()

# Validate resolution choice
if user_res not in ['360p', '720p']:
    print('Invalid resolution choice. Please restart the script and choose either 360P or 720P.')
    exit()

print(f'...You chose {user_res} resolution.')

# Fetch all video links from the playlist
our_links = link_snatcher(url)
if not our_links:
    print('No links found. Exiting.')
    exit()

os.chdir(BASE_DIR)

# Create a new folder named after the playlist ID
new_folder_name = foldertitle(url)
if not new_folder_name:
    print('Failed to create folder. Exiting.')
    exit()

folder_path = new_folder_name[:7]
try:
    os.mkdir(folder_path)
except FileExistsError:
    print('Folder already exists.')

os.chdir(folder_path)
SAVEPATH = os.getcwd()
print(f'\nFiles will be saved to {SAVEPATH}')

# List existing files to avoid re-downloading
existing_files = [f for f in os.listdir() if os.path.isfile(f)]

print('\nConnecting...')

# Download each video in the chosen resolution
for idx, link in enumerate(our_links, start=1):
    try:
        yt = YouTube(link)
        main_title = f"{idx:03d} - {yt.title}.mp4"  # Keep the file extension in title
        main_title = sanitize_filename(main_title)  # Sanitize the title
    except Exception as e:
        print(f'Error connecting to YouTube: {e}')
        continue

    if main_title not in existing_files:
        try:
            # Try to download in the chosen resolution first
            vid = yt.streams.filter(progressive=True, file_extension='mp4', res=user_res).first()
            if not vid and user_res == '720p':
                # If 720p is not available, try to download in 360p
                vid = yt.streams.filter(progressive=True, file_extension='mp4', res='360p').first()
                if vid:
                    print(f'720p not available. Downloading {main_title} in 360p ({round(vid.filesize / (1024 * 1024), 2)} MB)')
                else:
                    print(f'360p also not available for {main_title}. Skipping...')
                    continue
            elif not vid and user_res == '360p':
                print(f'{user_res} resolution not available for {main_title}. Skipping...')
                continue
            
            if vid:
                print(f'Downloading {main_title} ({round(vid.filesize / (1024 * 1024), 2)} MB)')
                vid.download(SAVEPATH, filename=main_title)
                print('Video downloaded')
        except Exception as e:
            print(f'Error downloading video: {e}')
    else:
        print(f'\nSkipping "{main_title}" as it already exists.\n')

print('Downloading finished')
print(f'\nAll your videos are saved at {SAVEPATH}')

