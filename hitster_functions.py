import hitster_config as c

def create_tables():
    # Create a table if it doesn't exist
    c.cursor.execute('''
    -- Create a table if it doesn't exist for songs
    CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY,
        url TEXT,
        artist TEXT,
        title TEXT,
        year INTEGER
    );
    ''')
    c.conn.commit()
    c.cursor.execute('''
    -- Create a table if it doesn't exist for packs
    CREATE TABLE IF NOT EXISTS packs (
        id INTEGER PRIMARY KEY,
        name TEXT
    );
    ''')
    c.conn.commit()
    c.cursor.execute('''
    -- Create a table to manage the relationship between songs and packs (many-to-many)
    CREATE TABLE IF NOT EXISTS song_pack (
        song_id INTEGER,
        pack_id INTEGER,
        FOREIGN KEY(song_id) REFERENCES songs(id),
        FOREIGN KEY(pack_id) REFERENCES packs(id),
        PRIMARY KEY (song_id, pack_id)
    );
    ''')
    c.conn.commit()
    
def init_packs():
    # Check if any packs exist
    existing_packs = get_packs()

    if not existing_packs:
        # If no packs exist, create a default one
        c.cursor.execute('''INSERT INTO packs (name) VALUES (?)''', ('Default',))
        c.conn.commit()
    else:
        c.cursor.execute('''SELECT id FROM packs WHERE name = ?''', (existing_packs[0][0],))
        c.selected_pack_id = c.cursor.fetchone()[0]
        
def add_pack():
    new_pack_name = c.simpledialog.askstring("Add Pack", "Wähle einen Namen für die neue Kategorie:")
    if new_pack_name:
        isValid = validate_pack_name(new_pack_name)
        if isValid:
            c.cursor.execute('''INSERT INTO packs (name) VALUES (?)''', (new_pack_name,))
            c.conn.commit()
            # Update the dropdown menu with the new pack
            c.pack_dropdown['values'] = get_packs()  # Update dropdown options (replace with your retrieval logic)
            c.pack_dropdown.set(new_pack_name)
            select_pack('')

def edit_pack():
    new_pack_name = c.simpledialog.askstring("Edit Pack Name", "Wähle einen neuen Namen für die Kategorie:")
    if new_pack_name:
        isValid = validate_pack_name(new_pack_name)
        if isValid:    
            c.cursor.execute('''UPDATE packs SET name = ? WHERE name = ?''', (new_pack_name, c.selected_pack_name))
            c.conn.commit()
            c.selected_pack_name = new_pack_name
            # Update the dropdown menu with the new pack
            c.pack_dropdown['values'] = get_packs()  # Update dropdown options (replace with your retrieval logic)
            c.pack_dropdown.set(new_pack_name)
            
def validate_pack_name(name):
    # Check if the pack already exists
    c.cursor.execute('''SELECT * FROM packs WHERE name = ?''', (name,))
    existing_pack = c.cursor.fetchone()
    if existing_pack:
        c.messagebox.showerror("Error", "Diese Kategorie existiert bereits!")
        return False
    elif c.re.match("^[a-zA-Z0-9_ ]+$", name) is None:
        c.messagebox.showerror("Error", "Kategorie-Name darf keine Sonderzeichen enthalten!")
        return False
    else:
        return True

def delete_pack():
    delete_all()
    c.cursor.execute('''DELETE FROM packs WHERE name = ?''', (c.selected_pack_name,))
    c.conn.commit()
    # Update the dropdown menu with the updated packs
    packs = get_packs()  # Replace this with your retrieval logic
    c.pack_dropdown['values'] = packs
    if not packs:
        c.cursor.execute('''INSERT INTO packs (name) VALUES (?)''', ('Default',))
        c.conn.commit()
        c.pack_dropdown['values'] = get_packs()  # Update dropdown options
        c.pack_dropdown.set('Default')  # Set the selection to 'Default'
    else:
        c.pack_dropdown.set(c.pack_dropdown['values'][0])  # Set the selection to the first pack
    select_pack('')

def load_songs():
    # Clear the existing table content
    c.song_table.delete(*c.song_table.get_children())
    # Retrieve songs belonging to the selected pack
    c.cursor.execute('''SELECT songs.* FROM songs
                      JOIN song_pack ON songs.id = song_pack.song_id
                      WHERE song_pack.pack_id = ?''', (c.selected_pack_id,))
    c.display_songs = c.cursor.fetchall()
    
    if len(c.display_songs) == 0:
        c.export_button.config(state=c.tk.DISABLED)
    else:
        c.export_button.config(state=c.tk.NORMAL)
    
    # Insert songs into the table
    for song in c.display_songs:
        c.song_table.insert("", c.tk.END, values=song[2:])
        
def select_pack(event):
    # Access the selected value from the combobox
    c.selected_pack_name = c.pack_dropdown.get()
    c.cursor.execute('''SELECT id FROM packs WHERE name = ?''', (c.selected_pack_name,))
    c.selected_pack_id = c.cursor.fetchone()[0]
    load_songs()

def get_packs():
    # Retrieve pack names from the database
    c.cursor.execute('''SELECT name FROM packs''')
    packs = c.cursor.fetchall()
    return packs

def fetch_spotify_data():
    try:
        # Get text from the clipboard
        url = c.pyperclip.paste()
    except:
        url = ''
    
    if "open.spotify.com/" not in url:
        c.messagebox.showerror("Error", c.invalid_url_error)
        return
    if "track" in url:
        track_id = url.split("/")[-1].split("?")[0]  # Extract track ID from link
        fetch_track(track_id)
    elif "playlist" in url:
        playlist_id = url.split("/")[-1].split("?")[0]  # Extract track ID from link
        fetch_playlist(playlist_id)
    else:
        c.messagebox.showerror("Error", c.invalid_url_error)
        return

# Function to fetch song details from Spotify API
def fetch_track(id):
    try:
        track_info = c.sp.track(id)
    except c.spotipy.SpotifyException as e:
        c.messagebox.showerror("Error", f"Song konnte nicht geladen werden: {e}")
    was_added = add_song(track_info, c.selected_pack_id)
    if was_added:
        c.song_table.insert("", c.tk.END, values=(track_info['artists'][0]['name'], track_info['name'], int(track_info['album']['release_date'][:4]) if track_info['album']['release_date'] else None))
    
def fetch_playlist(id):
    try:
        playlist = c.sp.playlist(id)
        tracks = playlist['tracks']['items']
        for track in tracks:
            add_song(track['track'], c.selected_pack_id)
        load_songs()
        
    except c.spotipy.SpotifyException as e:
        c.messagebox.showerror("Error", f"Playlist konnte nicht geladen werden: {e}")

def add_song(track_info, pack_id):
    id = track_info['id']
    artist = track_info['artists'][0]['name']
    title = track_info['name']
    year = int(track_info['album']['release_date'][:4]) if track_info['album']['release_date'] else None
    url = track_info['external_urls']['spotify']

    # Check if the song link exists in any pack
    c.cursor.execute('''SELECT * FROM songs WHERE url = ?''', (url,))
    existing_song = c.cursor.fetchone()
    if existing_song:
        existing_song_id = existing_song[0]
        c.cursor.execute('''SELECT pack_id FROM song_pack WHERE song_id = ?''', (existing_song_id,))
        existing_pack_id = c.cursor.fetchone()
        
        if existing_pack_id and existing_pack_id[0] != pack_id:
            c.cursor.execute('''INSERT INTO song_pack (song_id, pack_id) VALUES (?, ?)''', (existing_song_id, pack_id))
            c.conn.commit()

            # Append the details to the display_songs array
            c.display_songs.append(existing_song)
            return True
        else:
            c.messagebox.showerror("Error", "Dieser Song ist bereits in der Kategorie enthalten!")
            return False
    
    # Add fetched song details to the table and database
    c.cursor.execute('''INSERT INTO songs (artist, title, year, url) VALUES (?, ?, ?, ?)''', (artist, title, year, url))
    c.conn.commit()
    # Retrieve the last inserted row ID
    last_row_id = c.cursor.lastrowid

    # Fetch the details of the last inserted row
    c.cursor.execute('''SELECT * FROM songs WHERE id = ?''', (last_row_id,))
    last_entry = c.cursor.fetchone()

    # Append the details to the display_songs array
    if last_entry:
        c.display_songs.append(last_entry)
    
    # Associate the song with the specified pack
    c.cursor.execute('''SELECT id FROM songs WHERE url = ?''', (url,))
    song_id = c.cursor.fetchone()[0]
    c.cursor.execute('''INSERT INTO song_pack (song_id, pack_id) VALUES (?, ?)''', (song_id, pack_id))
    c.conn.commit()
    return True

def delete_song(artist, title, year):
    # Check if the song exists in any pack
    c.cursor.execute('''SELECT id FROM songs WHERE artist = ? AND title = ? AND year = ?''', (artist, title, year))
    song_id = c.cursor.fetchone()
    if song_id:
        song_id = song_id[0]
        c.cursor.execute('''SELECT pack_id FROM song_pack WHERE song_id = ?''', (song_id,))
        packs = c.cursor.fetchall()

        if len(packs) == 1:  # If the song is only in one pack
            c.cursor.execute('''DELETE FROM songs WHERE artist = ? AND title = ? AND year = ?''', (artist, title, year))
            c.conn.commit()
            c.cursor.execute('''DELETE FROM song_pack WHERE song_id = ?''', (song_id,))
            c.conn.commit()
        else:
            for pack in packs:
                pack_id = pack[0]
                if pack_id == c.selected_pack_id:
                    c.cursor.execute('''DELETE FROM song_pack WHERE song_id = ? AND pack_id = ?''', (song_id, pack_id))
                    c.conn.commit()
                    break

def delete_selected():
    selected_item = c.song_table.selection()
    if selected_item:
        for item in selected_item:
            values = c.song_table.item(item, "values")
            artist, title, year = values[0], values[1], values[2]
            delete_song(artist, title, year)
        load_songs()

def delete_all():
    if len(c.display_songs) > 0:
        for song in c.display_songs:
            delete_song(song[2], song[3], song[4])
        load_songs()