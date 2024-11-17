import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import simpledialog
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from reportlab.lib.pagesizes import mm
from reportlab.pdfgen import canvas
import qrcode
import random
import subprocess
import re
import pyperclip

def init_sp():
    # Spotify API credentials
    client_id = '8bfaa89f76bc4b03b26c5b5ca72cdae1'
    client_secret = 'fb735f3180ff438ba4801ad2f45bc558'
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Initialize and connect to the SQLite database
conn = sqlite3.connect('songs_database.db')
cursor = conn.cursor()

sp = init_sp()

song_table = ''
url_input = ''
pack_dropdown = ''
export_button = ''

selected_pack_name = 'Default'
selected_pack_id = 1

display_songs = []

invalid_url_error = '''
Gib bitte eine gültige Spotify URL an!

Wie findet man Spotify URLs:
1. Suche den Song bzw. die Playlist in Spotify
2. Rechts-Klick auf den Song bzw. die Playlist oder Klick auf die 3 Punkte
3. Gehe auf "Teilen" und dann "Songlink/Playlistlink kopieren"
'''