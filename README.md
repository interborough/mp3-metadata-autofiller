# MP3 Metadata Autofiller
A Python script that uses the Spotify Web API to add album art to and fill in an MP3 file's metadata. 

This script will prompt you for one or more MP3 files through a file selection menu. After selecting your files, the script queries Spotify's API and embeds the relevant metadata (song name, song artist, album name, album artist, track, number, disk number, album art, etc.) that is obtained from Spotify into the MP3 files. 

# Differences Between autofiller.py and autofiller_sacad.py
You might have noticed that there are two scripts - autofiller.py and autofiller_sacad.py. 

The Spotify API has a maximum album art size of 640x640 pixels, which is rather small. Due to this fact, I created an alternate script that uses the Smart Automatic Cover Art Downloader (SACAD), which allows the user to manually specify an album art size to target. However, SACAD searches the internet for album art instead of directly querying an existing catalog of art like Spotify, meaning that the time it takes for the script to execute is greatly increased. Additionally, I cannot guarantee that I'll be able to offer much support if you run into any issues with SACAD. Nevertheless, I would like to thank the author of SACAD for creating such a useful tool, and SACAD's Github page can be found at the following link: https://github.com/desbma/sacad.

Essentially, if you value faster performance and don't care about the smaller album art size, use autofiller.py. If you'd like to have more control over the size of the album art used and don't mind running into the occasional error, try out autofiller_sacad.py. 

# Dependencies
For this program to function correctly you must have Python installed, along with the spotipy, mutagen, and keyboard libaries for Python.

- Download Python: https://www.python.org/downloads/
- Install spotipy: `pip install spotipy`
- Install mutagen: `pip install mutagen`
- Install keyboard: `pip install keyboard`

For the SACAD album art version of this program you must additionally have the sacad library for Python installed.

- Install sacad: `pip install sacad`

# First Time Setup
- Download and install Python, along with the other relevant dependencies as outlined above. 
- Download the zip file of the mp3-metadata-autofiller Github archive, and extract it to a folder. 
- Create a Spotify account (if you don't have one already), log in, and navigate to the following link: https://developer.spotify.com/dashboard/
- Click on the "Create an App" button on the top right corner of the page. 
- Enter a name and description for your app (it can be anything you'd like) and click on the "Create" button.
- You should be redirected to a seperate page for your app. Underneath the title and description for your app, there should be a "Client ID", and a "Client Secret" value (you may have to click the text labeled "Show Client Secret" to see the Client Secret value). 
- Edit lines 29 and 30 in the autofiller.py script (or lines 30 and 31 if you're using autofiller_sacad.py), replacing the "PLACEHOLDER" text with your Client ID and Client Secret values (ex: `client_id = "PLACEHOLDER"` should become `client_id = "YOUR_CLIENT_ID_VALUE"`, and `client_secret = "PLACEHOLDER"` should become `client_secret = "YOUR_CLIENT_SECRET_VALUE"`, where you substitute in your Cilent ID and Client Secret values accordingly). 

# How to Use
- Complete the steps outlined in the "First Time Setup" section above. 
- Run a terminal window in the folder that you extracted the zip file to, and enter `python autofiller.py` (or `python autofiller_sacad.py` if you're using that script).
- A file selection window will appear. Select the MP3 files that you wish to find metadata for. Ensure that the names of these files are in the following format: `Artist Name - Track Name` (ex: `Billy Joel - Tell Her About It`). 
- If you are using autofiller_sacad.py, you will also be required to enter in an album art resolution to target. This will have a 25% margin of error, meaning that if your desired size cannot be found, artwork within the range of 25% larger or smaller than your target size will also be accepted.  

# Troubleshooting
If the script is unable to locate a song or is getting incorrect information, here are a few things to try or take note of. 

- Ensure that the song you are looking for is actually on Spotify.
- Make sure that your artist and track name information is accurate.
    - ex: `YOASOBI - Yasashii Suisei` is not found, but `YOASOBI - 優しい彗星` is found. Both of these titles refer to the same song, but Spotify uses Japanese instead of English to title the song. 
- The Spotify API has a query limit, meaning you can only make a certain number of queries in a given time period in order to avoid overloading the Spotify servers. I'm not entirely sure what this limit is, so as long as you don't try to get metadata for a huge amount of songs at once you should be fine. 
- A bug exists in the Spotify API itself. If a song title has special characters (things like apostrophes, quotation marks, or non-English letters), and you provide both the song title and the artist into a search query, then the query will break and always return no results. To solve this issue, this script checks whether a song title has special characters, and only searches using the song title if this is the case. This works as intended. However, this means that if your song has both special characters and a very commonly used song title, then Spotify may confuse the song you are looking for with another song with the same title. In this case, try removing the special character from the title to see if this improves the situation. Other than that, however, there's not much I can do about the issue seeing as the bug exists within the API itself.
    - ex: `Eddie Money - Shakin'` has an apostrophe in its title, and the query is therefore done by using only the song title. However, since `Shakin'` is a common song name, the incorrect metadata is embedded into the file. To fix this, remove the apostrophe from the song title and run the script again. This will fetch the correct information in this specific case, but may not work with every song that runs into this issue.  
- Some songs on Spotify aren't available in all markets. The Spotify search function searches the US market by default, but if you're not finding your song you can override this behavior. To do this, edit lines 102 and 104 of the autofiller.py script (or lines 128 and 128 in autofiller_sacad.py) to include a "market" parameter in the search query. 
    - ex: `track_query = spotify.search(q="artist:" + song.artist + " track:" + song.title, limit=1)` can become `track_query = spotify.search(q="artist:" + song.artist + " track:" + song.title, limit=1, market="GB")` to search the Great Britain market.
    - A list of valid market values can be found at the following link: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
