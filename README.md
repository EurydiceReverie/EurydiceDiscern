<img src='https://svgshare.com/i/17vg.svg' title='Eurydice' height="150">

EurydiceDiscern
===============

<!-- ABOUT Eurydice -->

Eurydice is a versatile music recognition tool written in Python that can identify and tag unknown audio files by using multiple services.


<!-- GETTING STARTED -->
## Getting Started

Follow these steps to get a local copy of Eurydice up and running:

### Prerequisites

* Python 3.11.7(Tested)🚀, though Python 3.9 is highly recommended

### Installation

1. Clone the repo
    ```shell
    git clone https://github.com/EurydiceReverie/EurydiceDiscern.git && cd EurydiceDiscern
    ```
2. Install all requirements
   ```shell
   pip install -r requirements.txt
   ```
3. Run the program at least once, or use this command
   ```shell
   python Eurydiceko.py
   ```
4. If you get error like:  
   **ModuleNotFoundError: No module named 'acrcloud.recognizer'**
   then :
   | Option | Command |
   |---|---|
   | Install ACRCloud SDK | `pip install --force-reinstall git+https://github.com/acrcloud/acrcloud_sdk_python.git` |
   | Install ACRCloud Extra Tools | `pip install --force-reinstall git+https://github.com/acrcloud/acrcloud_extr_tools.git` |

   
   ➕ If not, goto your python (or) env directory --> Lib\site-packages|
    
   ➕ Remove the acrcloud related two folders like (acrcloud, acrcloud-2.0.dist-info) and unzip the file named(Acrcloud.7z) from this repo and paste them in site-packages|

5. Usage/Run - python eurydiceko.py

## Configuration                           
In config\config.json make sure to specify your keys for authentication purpose :D                     
`"ACR"`: {                     
        `"HOST"`: "",                             
        `"ACCESS_KEY"`: "",                           
        `"ACCESS_SECRET"`: ""                           
    },                          
    `"Spotify"`: {                              
        `"CLIENT_ID"`: "",                          
        `"CLIENT_SECRET"`: ""                                 
    }                                     

## Audio source selection                                                                               
Please select the audio source you'd like to use:                         
+-------------------------------------------------------------------+                              
| 1: Microphone - Live audio capture                               |                          
| 2: Internal Sound - Detect sounds playing internally on the device|                               
| 3: File - Detect through an internally saved file                |                                   
+-------------------------------------------------------------------+                                    
Enter your choice (1, 2, or 3) and press Enter:      
----------------------------------------------->

  **Microphone Input** 🎤:                    
+----------------------            
Description: Identifies the music playing around you in real-time using your computer's microphone.                     
Ideal for: Quickly recognizing songs playing in the background, at events, or on the radio.                         
------------------------------------------------------------------------------------------->                    

  **Soundcard Capture** 🎧:                   
+----------------------                   
Description: Analyzes the audio output from your soundcard, identifying the music currently playing through your computer's speakers or headphones.               
Ideal for: Identifying music from streaming services, media players, or other applications.                                       
------------------------------------------------------------------------------------------->                   

> **⚠️ Important: Selecting Sound Input**

> When choosing this option, a list of available sound drivers on your PC will appear. Ensure you select "Stereo Mix" as your input source. 

> Why Stereo Mix?

> * **Sound Card Output = Stereo Mix Input:** Stereo Mix captures your computer's audio output directly, allowing you to identify music playing from any application. 

> If you don't see Stereo Mix listed, you may need to enable it in your sound settings.                               

 
  **File Identification** 📁:            
+----------------------                   
Description: Processes audio files from your test_file directory to identify the music they contain.                                 
Ideal for: Tags unknown or unorganized music files (like album_cover, MetaData, Synced Lyrics) to **unknown_file.audio_format** in your collection.       
------------------------------------------------------------------------------------------->      

## Working(Demo)
- `File Identification` : [This is Heaven - Nick Jonas](https://music.apple.com/sk/album/this-is-heaven/1554879162?i=1554879280)              

![File Identification](https://raw.githubusercontent.com/EurydiceReverie/EurydiceDiscern/main/assets/File_Audio_Recognition_guide.mp4)            

- `Internal Audio Capture` : [Houdini - Dua Lipa](https://music.apple.com/sk/album/houdini/1714502820?i=1714502827)

![Internal Audio Capture](https://raw.githubusercontent.com/EurydiceReverie/EurydiceDiscern/main/assets/Internal_audio_Recognition_guide.mp4)

- `Microphone Capture` : [Silver Peru - Blue Panama](https://www.youtube.com/watch?v=cpH-jqzpOpQ)

![Microphone Capture](https://raw.githubusercontent.com/EurydiceReverie/EurydiceDiscern/main/assets/Mic_audio_Recognition_guide.mp4)


## Contact 💬
Karthik K (Project developed) - [@EurydiceReverie][contact via telegram](https://t.me/SchadenfreudeKK)

>Inspired from Orpheus
