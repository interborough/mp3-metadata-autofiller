import os
import sys
import asyncio

from string import ascii_letters, digits, whitespace

import keyboard
import sacad

import tkinter
from tkinter.filedialog import askopenfilenames

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError, TALB, TPE1, TPE2, TCON, TYER, TRCK, TIT2, APIC, TPOS


class Song:
    def __init__(self, title, artist, path):
        self.title = title
        self.artist = artist
        self.path = path


def main():
    # Replace these two variables with your own id values.
    client_id = "PLACEHOLDER"
    client_secret = "PLACEHOLDER"

    # Get track and artist names from all tracks.
    file_paths = get_input_files()
    song_list, wrong_file_extension, wrong_name_format = get_tracks_and_artists(file_paths)

    # Make sure user input is valid.
    input_validation(wrong_file_extension, wrong_name_format)

    resolution_target = input("Enter the album art resolution that you would like to target. (ex: Entering 1000 means "
                              "1000x1000 pixels).\n")

    # Get access to Spotify API.
    credentials_manager = SpotifyClientCredentials(client_id, client_secret)
    spotify = spotipy.Spotify(client_credentials_manager=credentials_manager)

    # Query Spotify API.
    error_list, no_genre_list, no_album_art = obtain_and_edit_metadata(song_list, spotify, resolution_target)

    print("\nScript complete! For more detailed information on what was edited see the console output above. \n")

    # Inform Users of Errors
    output_errors(error_list, no_genre_list, no_album_art)

    print("Thank you for using the MP3 Metadata Autofiller.")
    exit_routine()


def output_errors(error_list, no_genre_list, no_album_art):
    if len(error_list) > 0:
        print("Spotify was unable to find one or more of your songs, or was unable to get all relevant song "
              "data for those tracks. A list of skipped tracks will be output below. For tips on how to try and make "
              "these tracks work, see the \"Troubleshooting\" section on the Github page. \n")

        for song in error_list:
            print(f"{song.artist} - {song.title}")

        print()

    if len(no_genre_list) > 0:
        print("Spotify was unable to find genres for the songs listed below. You should add genres to these songs "
              "manually, since this means that Spotify has no genre data pertaining to the below artists. \n")

        for song in no_genre_list:
            print(f"{song.artist} - {song.title}")

        print()

    if len(no_album_art) > 0:
        print("The Smart Automatic Cover Art Downloader was unable to locate album art for the songs listed below. \n")

        for song in no_genre_list:
            print(f"{song.artist} - {song.title}")

        print()


def input_validation(wrong_file_extension, wrong_name_format):
    if len(wrong_file_extension) > 0:
        print("One or more of the files that you input are not MP3 files. A list of all offending files will be "
              "output below. Please run the script again, making sure to pass in only MP3 files. \n")

        for file in wrong_file_extension:
            print(file)

        print()
        exit_routine()

    if len(wrong_name_format) > 0:
        print("One or more of the filenames that you input are not in the following format: \"Artist Name - Track "
              "Name\". A list of all offending files will be output below. Please run the script again, making sure "
              "that all of your files have names in the aforementioned format. \n")

        for file in wrong_name_format:
            print(file)

        print()
        exit_routine()


def obtain_and_edit_metadata(song_list, spotify, resolution_target):
    error_list = []
    no_genre_list = []
    no_album_art = []
    cwd = os.getcwd() + "\\album_art"

    for song in song_list:
        print(f"\nAttempting to add metadata to {song.artist} - {song.title}.")

        # Having titles with special characters like " or ' in the search query will cause the artist filter to
        # break and therefore not return any results in the items array. Searching only by title in this case
        # bypasses this issue.
        if set(song.title).difference(ascii_letters + digits + whitespace):
            print(f"{song.artist} - {song.title} has special characters in its title. Searching Spotify by title "
                  f"only.")
            track_query = spotify.search(q=song.title, limit=1)
        else:
            track_query = spotify.search(q="artist:" + song.artist + " track:" + song.title, limit=1)

        # Get relevant song data from JSON query data.
        try:
            song_name = str(track_query['tracks']['items'][0]['name'])
            album_name = str(track_query['tracks']['items'][0]['album']['name'])
            release_year = str(track_query['tracks']['items'][0]['album']['release_date'])[:4]
            track_number = str(track_query['tracks']['items'][0]['track_number'])
            total_tracks = str(track_query['tracks']['items'][0]['album']['total_tracks'])
            disk_number = str(track_query['tracks']['items'][0]['disc_number'])
            album_artist = str(track_query['tracks']['items'][0]['album']['artists'][0]['name'])
        except IndexError:
            print(f"Failed to add metadata to {song.artist} - {song.title}!")
            error_list.append(song)
            continue

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

        if len(genres) == 0:
            no_genre_list.append(song)

        # Obtain album art using the Smart Automatic Cover Art Downloader.
        coroutine = sacad.search_and_download(album_name,
                                              album_artist,
                                              "jpg",
                                              int(resolution_target),
                                              cwd,
                                              size_tolerance_prct=25,
                                              amazon_tlds=(),
                                              no_lq_sources="False",
                                              preserve_format="False")

        print("Searching for album art using the Smart Automatic Cover Art Downloader. This might take a while.")
        album_art_found = asyncio.get_event_loop().run_until_complete(coroutine)

        if not album_art_found:
            no_album_art.append(song)

        album_art = cwd + ".jpg"

        # Embed metadata into file.
        try:
            mp3_file = MP3(song.path)
        except ID3NoHeaderError:
            mp3_file = mutagen.File(song.path, easy=True)
            mp3_file.add_tags()

        mp3_file['TIT2'] = TIT2(encoding=3, text=song_name)
        mp3_file['TPE1'] = TPE1(encoding=3, text=", ".join(song_artists))
        mp3_file['TALB'] = TALB(encoding=3, text=album_name)
        mp3_file['TPE2'] = TPE2(encoding=3, text=album_artist)
        mp3_file['TRCK'] = TRCK(encoding=3, text=track_number + "/" + total_tracks)
        mp3_file['TYER'] = TYER(encoding=3, text=release_year)
        mp3_file['TCON'] = TCON(encoding=3, text=", ".join(genres).title())
        mp3_file['TPOS'] = TPOS(encoding=3, text=disk_number)

        if album_art_found:
            mp3_file['APIC'] = APIC(
                encoding=3,
                mime='image/jpeg',
                type=3, desc=u'Cover',
                data=open(album_art, "rb").read()
            )

        mp3_file.save(v2_version=3)
        print(f"Added metadata to {song.artist} - {song.title} successfully!")

    return error_list, no_genre_list, no_album_art


def get_input_files():
    print("Please select the MP3 file(s) you wish to get metadata for. Ensure that the name of the file or files are "
          "in the following format: \"Artist Name - Track Name\" \n")
    tkinter.Tk().withdraw()
    files = askopenfilenames()

    return files


def get_tracks_and_artists(files):
    song_list = []
    wrong_file_extension = []
    wrong_name_format = []

    for file in files:
        file_name = str(file)
        head, tail = os.path.split(file_name)

        if not tail.endswith(".mp3"):
            wrong_file_extension.append(file)
            continue

        try:
            track_name = tail[tail.index("-") + 1: tail.index(".mp3")].strip()
            artist_name = tail[:tail.index("-")].strip()
            curr_song = Song(track_name, artist_name, file)
            song_list.append(curr_song)
        except ValueError:
            wrong_name_format.append(file)
            continue

    return song_list, wrong_file_extension, wrong_name_format


def exit_routine():
    print("Press the \"Q\" key to quit.")

    while True:
        if keyboard.is_pressed("q"):
            sys.exit(0)


main()
