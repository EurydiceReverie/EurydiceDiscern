from ShazamAPI import Shazam

def shazam_recognize_song(audio_file_path):
    with open(audio_file_path, 'rb') as file:
        mp3_file_content_to_recognize = file.read()
    
    shazam = Shazam(mp3_file_content_to_recognize)
    recognize_generator = shazam.recognizeSong()
    
    try:
        for result in recognize_generator:
            if result:
                data = result[1] if isinstance(result, tuple) else result
                print(data)
                return data
    except StopIteration:
        print("Finished recognizing the song.")
    return None