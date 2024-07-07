import requests
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
from mutagen.id3 import USLT
from acrcloud.recognizer import ACRCloudRecognizer
import json
import os

def download_album_cover(album_cover_url, save_path):
    response = requests.get(album_cover_url)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)

def embed_album_art(audio_file_path, album_cover_path):
    audio = MP3(audio_file_path, ID3=ID3)
    try:
        audio.add_tags()
    except error as e:
        pass
    with open(album_cover_path, 'rb') as album_art:
        audio.tags.add(
            APIC(
                encoding=3,
                mime='image/jpeg',
                type=3,
                desc=u'Cover',
                data=album_art.read()
            )
        )
    audio.save(v2_version=3)

def save_and_embed_album_cover(audio_file_path, artist_name, song_title, album_artwork_url_template):
    album_artwork_url = album_artwork_url_template.replace('{w}', '1400').replace('{h}', '1400')
    album_cover_path = os.path.splitext(audio_file_path)[0] + '_cover.jpg'
    download_album_cover(album_artwork_url, album_cover_path)
    embed_album_art(audio_file_path, album_cover_path)