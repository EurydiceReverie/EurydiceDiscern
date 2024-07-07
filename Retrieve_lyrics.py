import json
import requests
from musixmatch_api import Musixmatch, CaptchaError, UserTokenError
import re

musixmatch = Musixmatch(Exception)

def sanitize_filename(filename):
    return re.sub(r'[/\:*?"<>|]', '', filename)

def format_time(ts):
    minutes = int(ts // 60)
    seconds = int(ts % 60)
    hundredths = int((ts - int(ts)) * 100)
    return f'[{minutes:02d}:{seconds:02d}.{hundredths:02d}]'

def process_rich_sync_lyrics(rich_sync_lyrics_json):
    lrc_lines = []
    try:
        rich_sync_data = json.loads(rich_sync_lyrics_json)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

    for line in rich_sync_data:
        ts = format_time(line['ts'])
        lrc_line = f'{ts}{line["x"]}'
        lrc_lines.append(lrc_line)

    return '\n'.join(lrc_lines)

def get_lyrics_from_musicxmatch(artist_name, song_title):
    try:
        user_token = musixmatch.get_user_token()
        
        track_data = musixmatch.get_search_by_track(song_title, artist_name, "")
        if track_data:
            track_id = track_data['track_id']
            rich_sync_data = musixmatch.get_rich_sync_by_id(track_id)
            
            print(json.dumps(track_data, indent=2))
            print(json.dumps(rich_sync_data, indent=2))

            if rich_sync_data and 'richsync_body' in rich_sync_data:
                rich_sync_lyrics_json = rich_sync_data['richsync_body']
                lrc_lyrics = process_rich_sync_lyrics(rich_sync_lyrics_json)
                return lrc_lyrics
            else:
                print("No synced lyrics found.")
                return None
        else:
            print("Track not found in Musixmatch.")
            return None
    except (CaptchaError, UserTokenError) as e:
        print(f"Error while working with Musixmatch: {e}")
        return None

def get_lyrics(artist_name, song_title):
    print(f"Fetching lyrics for: {artist_name} - {song_title}")
    return get_lyrics_from_musicxmatch(artist_name, song_title)