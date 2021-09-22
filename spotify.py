import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

# set up spotify client
SPOTIPY_CLIENT_ID=os.environ.get('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET=os.environ.get('SPOTIPY_CLIENT_SECRET')
spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

def get_track_url(song_title):
    spotify_response = spotify.search(q=song_title, type='track')
    track_url = spotify_response['tracks']['items'][0]['preview_url']
    return track_url