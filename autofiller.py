import os
import sys

from string import ascii_letters, digits, whitespace

import tkinter
from tkinter.filedialog import askopenfilename

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError, TALB, TPE1, TPE2, TCON, TYER, TRCK, TIT2, APIC, TPOS

from urllib.request import urlopen


def main():
    # Replace these two variables with your own id values.
    client_id = "PLACEHOLDER"
    client_secret = "PLACEHOLDER"

    # Open MP3 file and get track name and artist.
    mp3_file = get_input_file()
    artist_name, track_name = get_track_and_artist(mp3_file)

    credentials_manager = SpotifyClientCredentials(client_id, client_secret)
    spotify = spotipy.Spotify(client_credentials_manager=credentials_manager)

    # Having titles with special characters like " or ' in the search query will cause the artist filter to
    # break and therefore not return any results in the items array. Searching only by title in this case
    # bypasses this issue.
    if set(track_name).difference(ascii_letters + digits + whitespace):
        print("Track name has special characters in its title. Searching Spotify by title only.")
        track_query = spotify.search(q=track_name, limit=1)
    else:
        track_query = spotify.search(q="artist:" + artist_name + " track:" + track_name, limit=1)

    # Get relevant song data from JSON query data.
    try:
        song_name = str(track_query['tracks']['items'][0]['name'])
        album_name = str(track_query['tracks']['items'][0]['album']['name'])
        release_year = str(track_query['tracks']['items'][0]['album']['release_date'])[:4]
        track_number = str(track_query['tracks']['items'][0]['track_number'])
        total_tracks = str(track_query['tracks']['items'][0]['album']['total_tracks'])
        disk_number = str(track_query['tracks']['items'][0]['disc_number'])
        album_artist = str(track_query['tracks']['items'][0]['album']['artists'][0]['name'])
        album_art = str(track_query['tracks']['items'][0]['album']['images'][0]['url'])
    except IndexError:
        print("Spotify was unable to find your song, or was unable to get all relevant song data. Please try again "
              "and/or make sure that your song is on Spotify.")
        sys.exit(1)

    # There can be multiple song artists and genres.
    song_artists = []
    artist_index = 0

    while True:
        try:
            curr_song_artist = str(track_query['tracks']['items'][0]['artists'][artist_index]['name'])
            song_artists.append(curr_song_artist)
            artist_index += 1
        except IndexError:
            break

    genre_query = spotify.search(q="artist:" + album_artist, type="artist", limit=1)
    genres = []
    genre_index = 0

    while True:
        try:
            curr_artist_genre = str(genre_query['artists']['items'][0]['genres'][genre_index])
            genres.append(curr_artist_genre)
            genre_index += 1
        except IndexError:
            break

    # Embed metadata into file.
    try:
        mp3_file = MP3(mp3_file)
    except ID3NoHeaderError:
        mp3_file = mutagen.File(mp3_file, easy=True)
        mp3_file.add_tags()

    mp3_file['TIT2'] = TIT2(encoding=3, text=song_name)
    mp3_file['TPE1'] = TPE1(encoding=3, text=", ".join(song_artists))
    mp3_file['TALB'] = TALB(encoding=3, text=album_name)
    mp3_file['TPE2'] = TPE2(encoding=3, text=album_artist)
    mp3_file['TRCK'] = TRCK(encoding=3, text=track_number + "/" + total_tracks)
    mp3_file['TYER'] = TYER(encoding=3, text=release_year)
    mp3_file['TCON'] = TCON(encoding=3, text=", ".join(genres).title())
    mp3_file['TPOS'] = TPOS(encoding=3, text=disk_number)

    album_art = urlopen(album_art)

    mp3_file['APIC'] = APIC(
        encoding=3,
        mime='image/jpeg',
        type=3, desc=u'Cover',
        data=album_art.read()
    )

    album_art.close()
    mp3_file.save(v2_version=3)
    print("Done!")


def get_input_file():
    print("Please select the MP3 file you wish to get metadata for. Ensure that the name of the file is in the "
          "following format: \"Artist Name - Track Name\"")
    tkinter.Tk().withdraw()
    file = askopenfilename()
    return file


def get_track_and_artist(file):
    file_name = str(file)
    head, tail = os.path.split(file_name)

    if not tail.endswith(".mp3"):
        print("Please make sure to pass in an MP3 file!")
        sys.exit(1)

    try:
        artist_name = tail[:tail.index("-")].strip()
        track_name = tail[tail.index("-") + 1: tail.index(".mp3")].strip()
    except ValueError:
        print("Ensure that the name of the file is in the following format: \"Artist Name - Track Name\"")
        sys.exit(1)

    return artist_name, track_name


main()
