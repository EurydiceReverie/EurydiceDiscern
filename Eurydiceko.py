# -- coding: utf-8 --

print('''

███████╗██╗   ██╗██████╗ ██╗   ██╗██████╗ ██╗ ██████╗███████╗
██╔════╝██║   ██║██╔══██╗╚██╗ ██╔╝██╔══██╗██║██╔════╝██╔════╝
█████╗  ██║   ██║██████╔╝ ╚████╔╝ ██║  ██║██║██║     █████╗  
██╔══╝  ██║   ██║██╔══██╗  ╚██╔╝  ██║  ██║██║██║     ██╔══╝  
███████╗╚██████╔╝██║  ██║   ██║   ██████╔╝██║╚██████╗███████╗
╚══════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═════╝ ╚═╝ ╚═════╝╚══════╝                                                                    

                                                             ''')

import base64, os, eyed3, requests, json, re, numpy as np, sounddevice as sd, scipy.io.wavfile, acrcloud, eyed3.id3.frames, time
from eyed3.id3.frames import UserTextFrame
from bs4 import BeautifulSoup
from genius_api import GeniusApi
from itertools import cycle
from shutil import get_terminal_size
from threading import Thread
from time import sleep
from my_shazam_utility import shazam_recognize_song
from applemusic_api import AppleMusicApi
from Acrcloudretrieve import recognize_song, set_id3_tags_mp3
from Retrieve_lyrics import get_lyrics
from erhalten_alb_covers import save_and_embed_album_cover
from loader import Loader
from time import sleep

def load_config():
    with open('/config/config.json', 'r') as config_file:
        config_data = json.load(config_file)
    return config_data

config = load_config()

CLIENT_ID = config['Spotify']['CLIENT_ID']
CLIENT_SECRET = config['Spotify']['CLIENT_SECRET']

genius_api = GeniusApi()

def get_audio_source_choice():
    border = "=" * 50
    title = "AUDIO SOURCE SELECTION"
    padded_title = title.center(len(border))
    print(f"\n{border}")
    print(padded_title)
    print(border)
    box_width = max(len(s) for s in ["Microphone - Live audio capture",
                                     "Internal Sound - Detect sounds playing internally on the device",
                                     "File - Detect through an internally saved file"]) + 6
    print("\nPlease select the audio source you'd like to use:\n")
    print(f"+{'-' * (box_width - 2)}+")
    print(f"| 1: Microphone - Live audio capture{' ' * (box_width - len(' 1: Microphone - Live audio capture') - 3)}|")
    print(f"| 2: Internal Sound - Detect sounds playing internally on the device{' ' * (box_width - len(' 2: Internal Sound - Detect sounds playing internally on the device') - 3)}|")
    print(f"| 3: File - Detect through an internally saved file{' ' * (box_width - len(' 3: File - Detect through an internally saved file') - 3)}|")
    print(f"+{'-' * (box_width - 2)}+")
    choice = input("Enter your choice (1, 2, or 3) and press Enter: ")
    if choice in ['1', '2', '3']:
        with Loader(chan="Main", desc="Welcome…", mode='std2') as loader:
            time.sleep(10)
            loader.stop()
    else:
        print("Invalid choice, please enter 1, 2, or 3.")   
    print(f"Your choice was: {choice}")
    print(f"{border}\n")
    return choice

def capture_internal_audio(device, duration=10, sample_rate=44100, filename="internal_audio.wav"):
    device_info = sd.query_devices(device, 'input')
    max_input_channels = device_info.get('max_input_channels', 1)
    channels = min(2, max_input_channels)
    print(f"Capturing internal audio using {channels} channel(s).\n Please play the audio you'd like to identify…")
    with Loader(chan="Main", desc="Recording…", mode='std1') as loader:    
        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=2, dtype='float64', device=device)
        sd.wait()
        loader.stop()
    
    scipy.io.wavfile.write(filename, sample_rate, (recording * 32767).astype(np.int16))
    print("Capture complete.")
    print(f"Recording shape (samples, channels): {recording.shape}")
    print(recording, sample_rate)
    print(filename)
    return filename

def capture_and_save_audio_from_mic(duration=10, sample_rate=44100, filename="temp_captured_audio_file.wav"):
    with Loader(chan="Main", desc="Recording…", mode='std1') as loader:
        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=2, dtype='int16')
        sd.wait()
        loader.stop()
    
    print("Recording stopped.")
    scipy.io.wavfile.write(filename, sample_rate, recording)
    print(f"Recorded (samples, channels): {recording.shape}")
    print(recording, sample_rate)
    print(filename)
    return filename

def get_user_choice():
    print("=" * 50)
    print("Welcome to the Song Recognition Service!")
    print("=" * 50)

    print("\nPlease select the recognition service you'd like to use:\n")
    print("  1: YoutubeACR - Fast and accurate music recognition")
    print("  2: Shazam - Discover music, artists, and lyrics in seconds")
    
    print("-" * 50)

    choice = input("Enter your choice (1 or 2) and press Enter: ")
    with Loader(chan="Main", desc="Waiting…", mode='prog') as loader:
        time.sleep(5)

    print("\n" + "." * 25 + " Processing " + "." * 25 + "\n")
    return choice

def add_or_update_txxx_frame(audiofile, description, value):
    found = False
    frames = audiofile.tag.frame_set.get(eyed3.id3.frames.USERTEXT_FID, [])
    for frame in frames:
        if frame.description == description:
            frame.text = value
            found = True
            break

    if not found:
        new_frame = eyed3.id3.frames.UserTextFrame(description=description, text=value)
        if not frames:
            audiofile.tag.frame_set[eyed3.id3.frames.USERTEXT_FID] = [new_frame]
        else:
            frames.append(new_frame)

def authenticate_spotify(client_id, client_secret):
    auth_url = 'https://accounts.spotify.com/api/token'
    client_creds = f"{client_id}:{client_secret}"
    client_creds_b64 = base64.b64encode(client_creds.encode())
    headers = {'Authorization': f'Basic {client_creds_b64.decode()}'}
    data = {'grant_type': 'client_credentials'}
    response = requests.post(auth_url, headers=headers, data=data)
    access_token = response.json().get('access_token')
    return access_token

def search_spotify_for_song(access_token, artist_name, title):
    base_url = "https://api.spotify.com/v1/search"
    query = f"{title} artist:{artist_name}"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"q": query, "type": "track", "limit": 1}
    response = requests.get(base_url, headers=headers, params=params)
    results = response.json()
    try:
        track_info = results['tracks']['items'][0]
        return track_info
    except IndexError:
        print("Song not found on Spotify.")
        return None

def get_lyrics_from_genius(artist_name, title):
    results = genius_api.get_search_by_songs(f"{artist_name} {title}")
    if results:
        song_info = results[0]['result']  # Take the most relevant result
        song_id = str(song_info['id'])
        song_details = genius_api.get_song_by_id(song_id, text_format='plain')
        return song_details.get('lyrics', "Lyrics not available.")
    return "Song not found on Genius."

def save_lyrics_to_file(audio_file_path, track_number, title, artist_name, album_name, isrc, lyrics):
    base_directory = os.path.dirname(audio_file_path)
    file_name_format = f"{track_number:02d}. {title} - {artist_name} - {album_name} - {isrc}.lrc"
    safe_file_name = re.sub(r'[/:*?"<>|]', '', file_name_format)
    lyrics_file_path = os.path.join(base_directory, safe_file_name)
    with open(lyrics_file_path, 'w', encoding='utf-8') as lrc_file:
        lrc_file.write(lyrics)   
    print(f"Lyrics saved as: {safe_file_name}")

def get_high_quality_album_art_url(song_info):
    images = song_info['album']['images']
    if not images:
        return None
    highest_quality_image = max(images, key=lambda x: x['width']*x['height'])
    return highest_quality_image['url']

def save_high_quality_album_art(image_url, file_path):
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with open(file_path, 'wb') as out_file:
                for chunk in response.iter_content(1024):
                    out_file.write(chunk)
            print(f"High quality album art saved: {file_path}")
            return True
        else:
            print("Could not download the album art.")
    except Exception as e:
        print(f"Error saving high-quality album art: {e}")
    return False

def embed_album_art_to_song(file_path, image_path):
    try:
        audiofile = eyed3.load(file_path)
        if audiofile.tag is None:
            audiofile.initTag()
        with open(image_path, 'rb') as img_file:
            audiofile.tag.images.set(3, img_file.read(), 'image/jpeg')
        audiofile.tag.save()
        print("High quality album art embedded into song.")
    except FileNotFoundError:
        print(f"Failed to embed album art - No such file: {image_path}")

def process_audio_file_with_spotify_search(audio_file_path):
    shazam_data = shazam_recognize_song(audio_file_path)
    if shazam_data:
        artist_name = shazam_data['track']['subtitle']
        title = shazam_data['track']['title']
        print(f"Identified Song: {artist_name} - {title}")
        
        access_token = authenticate_spotify(CLIENT_ID, CLIENT_SECRET)
        song_info = search_spotify_for_song(access_token, artist_name, title)
        
        if song_info:
            print(json.dumps(song_info, indent=4))
            print("\n///////////////////////////////\n")
            
            album_name = song_info['album']['name']
            album_url = song_info['album']['external_urls']['spotify']
            track_number = song_info['track_number']
            release_date = song_info['album']['release_date']
            isrc = song_info.get('external_ids', {}).get('isrc', "Not Available")
            label = song_info['label'] if 'label' in song_info else "Not Available"
            explicit = str(song_info['explicit']) if 'explicit' in song_info else "Not Available"
            genres = ", ".join(song_info['genres']) if 'genres' in song_info else "Not Available"
            author_url = song_info['artists'][0]['external_urls']['spotify'] if 'artists' in song_info else "Not Available"
            spotify_url = song_info['external_urls']['spotify']
            
            print(f"Track Number on Spotify: {track_number}")
            
            audiofile = eyed3.load(audio_file_path)
            if audiofile.tag is None:
                audiofile.initTag(version=eyed3.id3.ID3_V2_3)
            
            audiofile.tag.artist = artist_name
            audiofile.tag.album = album_name
            audiofile.tag.album_artist = artist_name
            audiofile.tag.title = title
            audiofile.tag.recording_date = release_date
            
            add_or_update_txxx_frame(audiofile, "Album URL", album_url)
            add_or_update_txxx_frame(audiofile, "Eurydice", "True")
            add_or_update_txxx_frame(audiofile, "Compilation", "KK")
            add_or_update_txxx_frame(audiofile, "Genre", genres)
            add_or_update_txxx_frame(audiofile, "Author URL", author_url)
            add_or_update_txxx_frame(audiofile, "Label", label)
            add_or_update_txxx_frame(audiofile, "Explicit", explicit)
            add_or_update_txxx_frame(audiofile, "ISRC", isrc)
            add_or_update_txxx_frame(audiofile, "Spotify URL", spotify_url)
            
            audiofile.tag.comments.set(f"ISRC: {isrc}, Label: {label}, Explicit: {explicit}")
            
            audiofile.tag.save()
            
            print(f"Metadata embedded into the file: {audio_file_path}")

            high_res_image_url = get_high_quality_album_art_url(song_info)
            
            if high_res_image_url:
                image_file_path = os.path.splitext(audio_file_path)[0] + ".jpg"
                if save_high_quality_album_art(high_res_image_url, image_file_path):
                    embed_album_art_to_song(audio_file_path, image_file_path)
                else:
                    print("Skipping album art embed due to download failure.")
            else:
                print("No album art available.")

            new_file_name = f"{track_number:02d}. {title} - {artist_name} - {album_name} - {isrc}.mp3"
            new_file_name = re.sub(r'[/:*?"<>|]', '', new_file_name)
            new_file_path = os.path.join(os.path.dirname(audio_file_path), new_file_name)
            os.rename(audio_file_path, new_file_path)
            print(f"File has been renamed to: {new_file_name}")

            new_image_file_path = os.path.splitext(new_file_path)[0] + ".jpg"
            os.rename(image_file_path, new_image_file_path)
            print(f"Album art file has been renamed to: {os.path.basename(new_image_file_path)}")

            lyrics = get_lyrics_from_genius(artist_name, title)
            if 'plain' in lyrics:
                lyrics_plain_text = lyrics['plain']
                print("Printing Lyrics:\n", lyrics_plain_text)
                save_lyrics_to_file(audio_file_path, track_number, title, artist_name, album_name, isrc, lyrics_plain_text)
                print("Lyrics file saved")
            else:
                print("No lyrics available to save.")

        else:
            print("Song not found on Spotify.")
    else:
        print("Song could not be identified.")

if __name__ == "__main__":
    audio_source_choice = get_audio_source_choice()
    if audio_source_choice == '3':
        user_choice = get_user_choice()
        audio_file_path = '/Test_file/Unknown_file.mp3'
        if user_choice == '1':
            print("\n" + "." * 15 + " ᴜsɪɴɢ YᴏᴜᴛᴜʙᴇACR " + "." * 15 + "\n")
            song_tags = recognize_song(audio_file_path)

            if song_tags:
                print(f'Song identified: {song_tags}')
                set_id3_tags_mp3(audio_file_path, song_tags)

                artist_name = song_tags.get('artists')[0].get('name')
                song_title = song_tags.get('title')
        
                safe_artist_name = re.sub(r'[/\:?"<>|]', '', artist_name)
                safe_song_title = re.sub(r'[/\:?"<>|]', '', song_title)
                new_file_name = f"{safe_artist_name} - {safe_song_title}.mp3"
        
                new_file_path = os.path.join(os.path.dirname(audio_file_path), new_file_name)
                os.rename(audio_file_path, new_file_path)
                print(f"File has been renamed to: {new_file_name}")

            else:
                print('Could not identify the song in YᴏᴜᴛᴜʙᴇACR.')

            apple_music_api = AppleMusicApi(Exception)
            apple_music_api.get_access_token()
            track_results = apple_music_api.search('songs', f"{artist_name} - {song_title}")
            if track_results:
                track_id = track_results[0]['id']
                album_artwork_url_template = track_results[0]['attributes']['artwork']['url']
                save_and_embed_album_cover(new_file_path, artist_name, song_title, album_artwork_url_template)
            else:
                print("Song not found on Apple Music.")
        
            lrc_lyrics = get_lyrics(safe_artist_name, safe_song_title)
            if lrc_lyrics:
                lrc_file_path = os.path.join(os.path.dirname(audio_file_path), f"{safe_artist_name} - {safe_song_title}.lrc")
                with open(lrc_file_path, 'w', encoding='utf-8') as lrc_file:
                    lrc_file.write(lrc_lyrics)
                print(f"Saved LRC file to: {lrc_file_path}")
            else:
                print("Could not get the lyrics.")

        elif user_choice == '2':
            print("\n" + "." * 15 + " ᴜsɪɴɢ Sʜᴀᴢᴀᴍ " + "." * 15 + "\n")
            song_tags = shazam_recognize_song(audio_file_path)
            print(song_tags)
            process_audio_file_with_spotify_search(audio_file_path)

        else:
            print("Invalid choice. Exiting....")
            exit()

    elif audio_source_choice == '1':
        audio_file_path = capture_and_save_audio_from_mic(duration=10, sample_rate=44100)
        print("Attempting to recognize using YᴏᴜᴛᴜʙᴇACR first…\n")
        song_tags = recognize_song(audio_file_path)
        use_acrcloud = True

        if song_tags is None:
            print("YᴏᴜᴛᴜʙᴇACR couldn't identify the song. Attempting recognition with Sʜᴀᴢᴀᴍ…\n")
            song_tags = shazam_recognize_song(audio_file_path)
            use_acrcloud = False

        if song_tags:
            if use_acrcloud:
                artist_name = song_tags.get('artists')[0].get('name')
                song_title = song_tags.get('title')
                print(f"Song recognized successfully from youtubeACR!\n Artist: {artist_name}, Song: {song_title}\n")
            else:
                artist_name = song_tags['track']['subtitle']
                title = song_tags['track']['title']
                access_token = authenticate_spotify(CLIENT_ID, CLIENT_SECRET)
                song_info = search_spotify_for_song(access_token, artist_name, title)
                if song_info:
                    album_name = song_info['album']['name']
                    track_number = song_info['track_number']
                    isrc = song_info.get('external_ids', {}).get('isrc', "Not Available")
                    print(f"Song recognized successfully by sha-spo!\n Artist: {artist_name}, Song: {track_number:02d}. {title}, Album: {album_name}, ISRC tag: {isrc}\n")

                else:
                    print(f"Song recognized successfully by Shazam!\n Artist: {artist_name}, Song: {title}\n")              

        else:
            print("Failed to recognize the song from the service.\n")

    elif audio_source_choice == '2':
        print("\nAvailable audio devices for capture:\n")
        devices = sd.query_devices()
        for index, device in enumerate(devices):
            print(f"{index}: {device['name']} - {'(Default)' if device['default_samplerate'] == device['default_low_output_latency'] else ''}")
    
        device_selection = input("Please enter the device index or name you wish to use for the capture: ").strip()

        try:
            device_selection = int(device_selection)
        except ValueError:
            pass

        audio_file_path = capture_internal_audio(device=device_selection, duration=10, sample_rate=44100)
        print("waiting....\n")
        print("Attempting to recognize using YᴏᴜᴛᴜʙᴇACR first…\n")
        song_tags = recognize_song(audio_file_path)
        use_acrcloud = True

        if song_tags is None:
            print("YᴏᴜᴛᴜʙᴇACR couldn't identify the song. Attempting recognition with Sʜᴀᴢᴀᴍ…\n")
            song_tags = shazam_recognize_song(audio_file_path)
            use_acrcloud = False

        if song_tags:
            if use_acrcloud:
                artist_name = song_tags.get('artists')[0].get('name')
                song_title = song_tags.get('title')
                print(f"Song recognized successfully from youtubeACR!\n Artist: {artist_name}, Song: {song_title}\n")
            else:
                artist_name = song_tags['track']['subtitle']
                title = song_tags['track']['title']
                access_token = authenticate_spotify(CLIENT_ID, CLIENT_SECRET)
                song_info = search_spotify_for_song(access_token, artist_name, title)
                if song_info:
                    album_name = song_info['album']['name']
                    track_number = song_info['track_number']
                    isrc = song_info.get('external_ids', {}).get('isrc', "Not Available")
                    print(f"Song recognized successfully by sha-spo!\n Artist: {artist_name}, Song: {track_number:02d}. {title}, Album: {album_name}, ISRC tag: {isrc}\n")

                else:
                    print(f"Song recognized successfully by Shazam!\n Artist: {artist_name}, Song: {title}\n")              

        else:
            print("Failed to recognize the song from the service.\n")

    else:
        with Loader(chan="Main", desc="Invalid Choice", mode='std3') as loader:
            time.sleep(20)
            loader.stop()
        exit();

print("\n" + "="*80)
print("Made by KK\nThanks for using")
print("Author - KK")
print("="*80 + "\n")