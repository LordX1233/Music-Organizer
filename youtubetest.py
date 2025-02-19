#INSTALL pytubefix FIRST (The same way you installed flet)
#FOR MAC: Open the terminal and run: pip3 install pytubefix
#FOR WINDOWS open your cmd and run: pip install pytubefix
#Yes, this code is from chat gpt but I have done this before but pytube was not working lol
from pytubefix import YouTube
import os

def download_audio(url, name, output_folder=r"Songs"):

    yt = YouTube(url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    print(f"Downloading: {yt.title}")
    # Ensure output directory exists
    os.makedirs(output_folder, exist_ok=True)
    # Download audio file
    audio_file = audio_stream.download(output_path=output_folder)
    # Convert to MP3
    mp3_file = os.path.join(output_folder, name + ".mp3")
    os.rename(audio_file, mp3_file)
    print(f"Downloaded and converted to MP3: {mp3_file}")

# Example usage
song_name = input("Enter song name: ")
video_url = input("Enter YouTube URL: ")
download_audio(video_url, song_name)