import hitster_config as c
import hitster_functions as f
import hitster_gen as gen

def generate_gui():
    # Create the main window
    root = c.tk.Tk()
    root.title("Hitster Erweiterungs-Generator")

    # Create a frame as a container
    container = c.tk.Frame(root, padx=10, pady=10)
    container.grid(row=0, column=0, sticky='nsew')
    container.grid_columnconfigure(0, weight=1)  # Allow column 0 to resize with the window
    container.grid_rowconfigure(1, weight=1)  # Allow column 0 to resize with the window

    # Pack management frame
    pack_frame = c.ttk.Frame(container)
    pack_frame.grid(row=0, column=0, sticky="ew")

    # Dropdown for selecting current pack
    pack_label = c.ttk.Label(pack_frame, text="Kategorie:")
    pack_label.grid(row=0, column=0, padx=5, pady=5)
    pack_var = c.tk.StringVar()
    c.pack_dropdown = c.ttk.Combobox(pack_frame, textvariable=pack_var, state='readonly')
    c.pack_dropdown['values'] = f.get_packs()
    c.pack_dropdown.bind('<<ComboboxSelected>>', f.select_pack)
    c.pack_dropdown.current(0)
    c.pack_dropdown.grid(row=0, column=1, padx=5, pady=5)

    # Buttons for pack management
    add_pack_button = c.ttk.Button(pack_frame, text="Kategorie Erstellen", command=lambda: f.add_pack())
    add_pack_button.grid(row=0, column=2, padx=5, pady=5)

    edit_pack_button = c.ttk.Button(pack_frame, text="Umbenennen", command=f.edit_pack)
    edit_pack_button.grid(row=0, column=3, padx=5, pady=5)

    delete_pack_button = c.ttk.Button(pack_frame, text="Löschen", command=f.delete_pack)
    delete_pack_button.grid(row=0, column=4, padx=5, pady=5)

    # Create a frame for the table
    table_frame = c.tk.Frame(container)
    table_frame.grid(row=1, column=0, sticky='nsew')
    table_frame.grid_rowconfigure(0, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)

    # Create a Treeview widget for the table
    columns = ("Künstler", "Titel", "Jahr")
    c.song_table = c.ttk.Treeview(table_frame, columns=columns, show="headings")

    # Configure column headings
    for col in columns:
        c.song_table.heading(col, text=col)
        c.song_table.column(col, width=150)  # Adjust column width as needed

    c.song_table.grid(row=0, column=0, sticky='nsew')

    # Create scrollbar
    scrollbar = c.tk.Scrollbar(table_frame, orient="vertical", command=c.song_table.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")

    # Link scrollbar to Treeview
    c.song_table.configure(yscrollcommand=scrollbar.set)  

    #row
    link_frame = c.tk.Frame(container)
    link_frame.grid(row=2, column=0, sticky='ew')

    link_label = c.ttk.Label(link_frame, text="Spotify Song/Playlist URL:")
    link_label.grid(row=0, column=0, sticky='w', padx=5, pady=5)

    # c.url_input = c.ttk.Entry(link_frame)
    # c.url_input.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
    # link_frame.grid_columnconfigure(1, weight=1)  # Allow column 0 to resize with the window

    # Create a style object
    button_style = c.ttk.Style()

    # Configure the button style
    button_style.configure("Custom.TButton", font=("Helvetica", 10, "bold"))

    # Apply the style to the button
    add_button = c.ttk.Button(link_frame, text="Aus der Zwischenablage Hinzufügen", command=lambda: f.fetch_spotify_data(), style="Custom.TButton")
    add_button.grid(row=0, column=2, sticky='we', padx=5, pady=5)

    #row
    delete_frame = c.tk.Frame(container)
    delete_frame.grid(row=3, column=0, sticky='ew')

    delete_button = c.ttk.Button(delete_frame, text="Auswahl Löschen", command=lambda: f.delete_selected())
    delete_button.grid(row=2, column=0, sticky='w', padx=5, pady=5)

    delete_all_button = c.ttk.Button(delete_frame, text="Alle Songs Löschen", command=lambda: f.delete_all())
    delete_all_button.grid(row=2, column=1, sticky='w', padx=5, pady=5)

    #row
    c.export_button = c.ttk.Button(container, text="Karten Exportieren", command=lambda: gen.export())
    c.export_button.grid(row=4, column=0, sticky='w', padx=5, pady=5)

    root.grid_columnconfigure(0, weight=1)  # Allow column 0 to resize with the window
    root.grid_rowconfigure(0, weight=1)  # Allow column 0 to resize with the window
    root.minsize(550, 300)  # Minimum width of 300 pixels and minimum height of 200 pixels
    root.geometry("550x300")  # Set initial size
    
    # Load existing songs from the database
    f.load_songs()

    root.mainloop()