import json
import eyed3
from acrcloud.recognizer import ACRCloudRecognizer

def load_config():
    with open('/config/config.json', 'r') as config_file:
        config_data = json.load(config_file)
    return config_data

config = load_config()

# Accessing the configuration values
ACR_HOST = config['ACR']['HOST']
ACR_ACCESS_KEY = config['ACR']['ACCESS_KEY']
ACR_ACCESS_SECRET = config['ACR']['ACCESS_SECRET']

recognizer = ACRCloudRecognizer({
    'host': ACR_HOST,
    'access_key': ACR_ACCESS_KEY,
    'access_secret': ACR_ACCESS_SECRET,
    'timeout': 10  # seconds
})

def recognize_song(audio_file_path):
    buffer = open(audio_file_path, 'rb').read()
    result = recognizer.recognize_by_filebuffer(buffer, 0)
    try:
        result_dict = json.loads(result)
        return result_dict['metadata']['music'][0]
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"Error while parsing result: {e}")
        return None

def set_id3_tags_mp3(audio_file_path, tags):
    audio_file = eyed3.load(audio_file_path)
    if not audio_file.tag:
        audio_file.initTag()

    audio_file.tag.artist = tags.get('artists')[0].get('name')
    audio_file.tag.album = tags.get('album').get('name')
    audio_file.tag.album_artist = tags.get('artists')[0].get('name')
    audio_file.tag.title = tags.get('title')

    release_date = tags.get('release_date')
    if release_date and len(release_date) >= 4:
        year_string = release_date[:4]
        try:
            year = int(year_string)
            if hasattr(eyed3.id3.tag, 'Date'):
                audio_file.tag.recording_date = eyed3.id3.tag.Date(year)
            else:
                audio_file.tag.setTextFrame("TDRC", year_string)
        except ValueError:
            print(f"Invalid date format in the tag: {release_date}")

    audio_file.tag.genre = tags.get('genres')[0].get('name')
    audio_file.tag.publisher = "KARTHIK"
    
    audio_file.tag.copyright = tags.get('label', '')
    audio_file.tag.comments.set(u"Explicit: Yes")  
    
    audio_file.tag.save(version=eyed3.id3.ID3_V2_3)

    audio_file.tag.save()