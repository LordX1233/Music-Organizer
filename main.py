import sqlite3
import flet as ft
import base64
import os
from pytubefix import YouTube
import shutil
import sys
import random
import threading

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'musicOrganizer.db')

def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  
    return conn

def get_asset_path(filename, subfolder="Assets"):
    if getattr(sys, 'frozen', False):
        base_path = os.path.join(sys._MEIPASS, subfolder)
    else:
        base_path = os.path.join(os.path.abspath(subfolder))
    return os.path.join(base_path, filename)


def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK
    page.title = 'Music Organizer'
    page.window.width = 1024
    page.window.height = 768
    page.window.resizable = False

    playing = False
    playing_playlist = False

    audio_player = ft.Audio(src=" ", autoplay=True)
    library_list = []
    playlist_list = []
    playlists = []
    current_song_index = 0
    current_playlist_id = 0

    def playsong(e, song):
        nonlocal playing, current_song_index, playing_playlist, playlist_list
        audio_player.src = get_asset_path(song, subfolder="Songs")
        playButton.content.icon = ft.Icons.PAUSE_SHARP
        playing = True
        audio_player.play()

        #? ChatGPT Did this cause I couldnt figure out why it was repeatin
        if playing_playlist:
            if current_song_index is None or playlist_list[current_song_index] != song:
                current_song_index = next(i for i, s in enumerate(playlist_list) if s == song)
        else:
            if current_song_index is None or library_list[current_song_index] != song:
                current_song_index = next(i for i, s in enumerate(library_list) if s == song)

                
        current_song_text.content.value = os.path.splitext(song)[0]
        audio_player.on_position_changed = lambda e: update_progress()
        page.update()
    
    def delete_song(e, song):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Songs WHERE name = ?", (os.path.splitext(song)[0],))
        conn.commit()
        os.remove(get_asset_path(song, subfolder="Songs"))
        songs_table_load()
        pass
        
    songs_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Song name", style=ft.TextStyle(color=ft.Colors.WHITE), width=490)),
            ft.DataColumn(ft.Text("", style=ft.TextStyle(color=ft.Colors.WHITE))),
        ],
        heading_row_color="black",
    ) 

    add_songs_table = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("",width=380)),
            ft.DataColumn(label=ft.Text("")),
        ],
        heading_row_height=0
    ) 

    edit_playlists_table = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Name",width=340)),
            ft.DataColumn(label=ft.Text("Cover")),
            ft.DataColumn(label=ft.Text("")),
        ],
        heading_row_color="black",
    ) 

    

    def edit_playlists_table_load():
        edit_playlists_table.rows.clear()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Playlists")
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            edit_playlists_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(row["name"], style=ft.TextStyle(color=ft.Colors.BLACK))), 
                    ft.DataCell(ft.Image(width=40, height=40, fit=ft.ImageFit.FILL, src_base64= row["image"])), 
                    ft.DataCell(ft.IconButton(ft.Icons.EDIT_SHARP, icon_color=ft.Colors.BLUE, on_click=lambda e, r=row: editPlaylistClicked(e, r))),
                ])
            )
        page.update()


    def add_songs_table_load():
        add_songs_table.rows.clear()
        for root, dirs, files in os.walk("Songs"):
            for file in files:
                file_name, _ = os.path.splitext(file) 
                add_songs_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(file_name, style=ft.TextStyle(color=ft.Colors.BLACK))), 
                        ft.DataCell(ft.IconButton(ft.Icons.ADD_CIRCLE, icon_color=ft.Colors.GREEN, on_click=lambda e, song=file_name: add_song_to_playlist(e, song))),
                    ])
                )
        page.update()
    
    def add_song_to_playlist(e, song):
        nonlocal current_playlist_id
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SongID FROM Songs WHERE name = ?", (song,))
        name_id = cursor.fetchone()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Song_Playlist (SongID, PlaylistID) VALUES (?, ?)", (name_id[0], current_playlist_id))
        conn.commit()
        edit_playlist_songs_table_load()
        page.update()
    

    def remove_song_from_playlist(e, song):
        nonlocal current_playlist_id

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SongID FROM Songs WHERE name = ? LIMIT 1", (song,))
        name_id = cursor.fetchone()
        
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM Song_Playlist
            WHERE rowid = (
                SELECT rowid FROM Song_Playlist WHERE SongID = ? AND PlaylistID = ? LIMIT 1
            )
        """, (name_id[0], current_playlist_id))
        conn.commit()
        edit_playlist_songs_table_load()
        page.update()
    
    edit_playlist_songs_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("", style=ft.TextStyle(color=ft.Colors.WHITE), width=405)),
            ft.DataColumn(ft.Text("", style=ft.TextStyle(color=ft.Colors.WHITE), width=58)),
        ],
        heading_row_height=0,
    )

    playlist_songs_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("", style=ft.TextStyle(color=ft.Colors.WHITE), width=400)),
        ],
        heading_row_height=0,
    )

    def edit_playlist_songs_table_load():
        nonlocal current_playlist_id
        edit_playlist_songs_table.rows.clear()

        playlist_id = current_playlist_id
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
        SELECT Songs.name
        FROM Songs
        JOIN Song_Playlist ON Songs.SongID = Song_Playlist.SongID
        WHERE Song_Playlist.PlaylistID = ?;
        """
        cursor.execute(query,(playlist_id,))
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            edit_playlist_songs_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(row[0], style=ft.TextStyle(color=ft.Colors.BLACK))), 
                    ft.DataCell(ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.RED, on_click=lambda e, f=row[0]: remove_song_from_playlist(e, f))),
                ])
            )
        page.update()

            
    def songs_table_load():
        songs_table.rows.clear()
        library_list.clear()

        conn = get_db_connection()
        cursor = conn.cursor()

        for root, dirs, files in os.walk("Songs"):
            for file in files:
                file_name, _ = os.path.splitext(file) 

                cursor.execute("SELECT 1 FROM Songs WHERE name = ?", (file_name,))
                result = cursor.fetchone()
                if not result:
                    cursor.execute("INSERT INTO Songs (name) VALUES (?)", (file_name,))
                    conn.commit() 
                songs_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(file_name, style=ft.TextStyle(color=ft.Colors.BLACK)), on_tap=lambda e, f=file: playsong(e, f)), 
                        ft.DataCell(ft.Icon(ft.Icons.DELETE, color=ft.Colors.RED), on_tap=lambda e, f=file: delete_song(e, f)),
                    ])
                )
                library_list.append(file)
        page.update()
    

    songs_scrollable_table = ft.ListView(
        controls=[songs_table],
        height=445,
        width=637,
        left=300,
        top=278.5,
        expand=True,
        visible=False
    )

    songs_table_load()
    add_songs_table_load()
    edit_playlists_table_load()
    edit_playlist_songs_table_load()


    def fetch_list_of_songs():
        pass

    def make_everything_invisible():
        row_covers.visible = playlistName.visible = playlistDescription.visible = playlistDeleteButton.visible = editPlaylists.visible = volume_slider.visible = current_song_text.visible = filenamedisplay.visible = addsongfile.visible = addsongButton.visible = youtubeLinkField.visible = songNameField.visible = coverImagePlaylist.visible = playlistSongsList.visible = playListSongs.visible = librarySongs.visible = songs_scrollable_table.visible = coverImage.visible = addplaylistButton.visible = playButton.visible = progress_bar.visible = rewindButton.visible = forwardButton.visible = shuffleButton.visible = playButtonPlaylist.visible = shuffleButtonPlaylist.visible = playlistCoverButton.visible = playlistNameField.visible = edit_playlistNameField.visible= playlistDescriptionField.visible = edit_playlistDescriptionField.visible = playlistSaveButton.visible = homeContainer.visible = False
        page.update()
    
    def homeScreen(e):
        lobbyDesign.src=get_asset_path("music player.png")
        make_everything_invisible()
        row_covers.visible = volume_slider.visible = current_song_text.visible = addplaylistButton.visible = playButton.visible = progress_bar.visible = rewindButton.visible = forwardButton.visible = shuffleButton.visible= homeContainer.visible = True
        playlist_display.controls.clear()
        update_side_playlists()
        update_row_covers()
        page.update()
        for playlist in playlists:
            playlist_display.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Image(src=playlist["cover"], width=100, height=100),
                    ft.Text(playlist["name"], color="white"),
                    ft.Text(playlist["description"], color="gray"),
                ], spacing=5),
                bgcolor="#333333",
                padding=10,
                border_radius=10
            )
        )
        page.update()


    def get_full_filename(song_name):
        for file in os.listdir("Songs"):
            file_name, ext = os.path.splitext(file)
            if file_name == song_name:
                return file_name + ext

    def playlistScreen(e, id):
        update_side_playlists()
        nonlocal playing_playlist, playlist_list
        lobbyDesign.src=get_asset_path("playlistScreen.png")
        make_everything_invisible()
        playlistName.visible = playlistDescription.visible = playButtonPlaylist.visible = shuffleButtonPlaylist.visible = coverImagePlaylist.visible = playlistSongsList.visible = True
        playing_playlist = True
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, description, image FROM Playlists WHERE PlaylistID = ?", (id,))
        details = cursor.fetchone()
        conn.close()
        coverImagePlaylist.src_base64 = details[2]
        playlistName.value = details[0]
        playlistDescription.value = details[1]


        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
        SELECT Songs.name
        FROM Songs
        JOIN Song_Playlist ON Songs.SongID = Song_Playlist.SongID
        WHERE Song_Playlist.PlaylistID = ?;
        """
        cursor.execute(query,(id,))
        rows = cursor.fetchall()
        conn.close()
        playlist_songs_table.rows.clear()
        playlist_list.clear()
        for row in rows:
            full_name = get_full_filename(row[0])
            playlist_songs_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(row[0], style=ft.TextStyle(color=ft.Colors.BLACK)), on_tap=lambda e, fu=full_name: playsong(e, fu)),
                ]))
            playlist_list.append(full_name)
        
        print(playlist_list)
            
        page.update()

    def createPlaylistScreen(e):
        lobbyDesign.src=get_asset_path("createPlaylist.png")
        make_everything_invisible()
        playlistCoverButton.visible = playlistNameField.visible = playlistDescriptionField.visible = playlistSaveButton.visible = playListSongs.visible = librarySongs.visible = True
        add_songs_table_load()
        page.update()

    def editPlaylistScreen(e):
        edit_playlists_table_load()
        lobbyDesign.src = get_asset_path("choosePlaylist.png")
        make_everything_invisible()
        editPlaylists.visible = True
        edit_playlists_table_load()
        update_side_playlists()
        page.update()

        #! para guardar el paylist
    def savePlaylist(e):
        conn = get_db_connection()
        cursor = conn.cursor()
        if coverImage.src_base64 == "":
            with open(get_asset_path("baseIcon.png"), "rb") as image_file:
                convertImgToString = base64.b64encode(image_file.read()).decode()
                coverImage.src_base64=convertImgToString
        cursor.execute("INSERT INTO Playlists (name, image, description) VALUES (?, ?, ?)", (playlistNameField.content.value, coverImage.src_base64,playlistDescriptionField.content.value))
        coverImage.src_base64 = playlistNameField.content.value = playlistDescriptionField.content.value = ""
        print("Added Succesfully")
        playlist_id = cursor.lastrowid
        cursor.execute("UPDATE Song_Playlist SET PlaylistID = ? WHERE PlaylistID = 0", (playlist_id,))
        conn.commit()
        conn.close()
        homeScreen(None)

        

    def editPlaylistClicked(e, row):
        nonlocal current_playlist_id
        update_side_playlists()
        lobbyDesign.src=get_asset_path("editPlaylist.png")
        make_everything_invisible()
        playlistDeleteButton.visible = coverImage.visible = playlistCoverButton.visible = edit_playlistNameField.visible = edit_playlistDescriptionField.visible = playListSongs.visible = librarySongs.visible = True
        edit_playlistNameField.content.value = row['name']
        edit_playlistDescriptionField.content.value = row['description']
        coverImage.src_base64 = row['image']
        current_playlist_id = row['PlaylistID']
        print(current_playlist_id)
        add_songs_table_load()
        edit_playlist_songs_table_load()
        page.update()

    def addSongClicked(e, file_path):
        update_side_playlists()
        nonlocal currentmusicfile
        if songNameField.content.value not in {os.path.splitext(song)[0] for song in library_list}:
            if youtubeLinkField.content.value == "":
                print(currentmusicfile)
                file_extension = os.path.splitext(file_path)[1]
                new_file_name = f"{ songNameField.content.value}{file_extension}"  # Rename using song_name
                destination = os.path.join("Songs", new_file_name)  # Define new path
                shutil.copy(file_path, destination)
                youtubeLinkField.content.disabled = False
                filenamedisplay.content.value = ""
                songNameField.content.value = ""
                currentmusicfile = ""
                addsongButton.visible = False
            else:
                try:
                    yt = YouTube(youtubeLinkField.content.value)
                    audio_stream = yt.streams.filter(only_audio=True).first()
                    os.makedirs("Songs", exist_ok=True)
                    audio_file = audio_stream.download(output_path="Songs")
                    mp3_file = os.path.join("Songs", songNameField.content.value + ".mp3")
                    os.rename(audio_file, mp3_file)
                    addsongfile.visible = True
                    filenamedisplay.content.value = ""
                    addsongButton.visible = False
                except:
                    filenamedisplay.content.color = 'red'
                    filenamedisplay.content.value = "Invalid Link"
        else:
            filenamedisplay.content.color = 'red'
            filenamedisplay.content.value = "Invalid Name"
        songs_table_load()
        print(library_list)
        page.update
        filenamedisplay.content.color = 'black'
        filenamedisplay.content.value = os.path.basename(currentmusicfile)
    
    def songsScreen(e):
        lobbyDesign.src=get_asset_path("songsScreen.png")
        make_everything_invisible()
        filenamedisplay.visible = addsongfile.visible = songs_scrollable_table.visible = songNameField.visible = youtubeLinkField.visible = True
        songs_table_load()
        page.update()
    
    def addSongFileClicked(e, page): 
        update_side_playlists()
        nonlocal currentmusicfile 
        if filenamedisplay.content.value == "":      
            def fileSelected(e: ft.FilePickerResultEvent):
                nonlocal currentmusicfile
                if e.files:
                    file = e.files[0]
                    filenamedisplay.content.value = file.name
                    currentmusicfile = file.path
                page.update()
            
            filePicker = ft.FilePicker(on_result=fileSelected)
            page.overlay.append(filePicker)
            page.update() 
            filePicker.pick_files(allow_multiple=False, allowed_extensions=["mp3", "wav"])
            youtubeLinkField.content.disabled = True
            youtubeLinkField.content.value = ""
        else:
            filenamedisplay.content.value = ""
            currentmusicfile = ""
            youtubeLinkField.content.disabled = False
            page.update()

    def check_add_change(e):
        nonlocal currentmusicfile
        if songNameField.content.value != "" and (youtubeLinkField.content.value != "" or currentmusicfile != ""):
            addsongButton.visible = True
        else:
            addsongButton.visible = False
        page.update()


    def playlistCoverClicked(e):
        print("choose the album cover")
        def fileSelected(e: ft.FilePickerResultEvent):
            if e.files:
                file = e.files[0]
                selected_image_path = file.path  
                with open(selected_image_path, "rb") as image_file:
                    convertImgToString = base64.b64encode(image_file.read()).decode()
                    coverImage.src_base64=convertImgToString
                coverImage.visible = True                
            page.update()

        filePicker = ft.FilePicker(on_result=fileSelected)
        page.overlay.append(filePicker)
        page.update()
        filePicker.pick_files(allow_multiple=False, allowed_extensions=["jpg", "png", "jpeg"])


    def update_progress():
        current_position = audio_player.get_current_position()
        duration = audio_player.get_duration()
        progress = 0
        if current_position != None and duration != None: progress = (current_position / duration)
        progress_bar.content.value = progress
        if current_position == duration:
            forward(None)
        page.update()
    

    def musicPlay(e):
        nonlocal playing
        if playing:
            playButton.content.icon = ft.Icons.PLAY_ARROW
            playing = False
            audio_player.pause()
        else:
            playButton.content.icon = ft.Icons.PAUSE_SHARP
            playing = True
            audio_player.resume()
        page.update()
        pass

    def shuffle(e):
        nonlocal playing_playlist, playlist_list
        if playing_playlist:
            random.shuffle(playlist_list)
            playsong(None, playlist_list[0])
            print(playlist_list)
        else:
            random.shuffle(library_list)
            playsong(None, library_list[0])
        
        if lobbyDesign.src == "music player.png":current_song_text.visible = True
        page.update()

    def rewind(e):
        nonlocal current_song_index, playing_playlist, playlist_list
        if playing_playlist:
            if audio_player.get_current_position() >= audio_player.get_duration()/2:
                playsong(None, playlist_list[current_song_index])
            else:
                if current_song_index - 1 != -1:
                    current_song_index -= 1
                    playsong(None, playlist_list[current_song_index])
                else:
                    playsong(None, playlist_list[current_song_index])
        else:
            if audio_player.get_current_position() >= audio_player.get_duration()/2:
                playsong(None, library_list[current_song_index])
            else:
                if current_song_index - 1 != -1:
                    current_song_index -= 1
                    playsong(None, library_list[current_song_index])
                else:
                    playsong(None, library_list[current_song_index])
            
        
    def forward(e):
        nonlocal current_song_index, playing_playlist, playlist_list
        if audio_player.playback_rate == 2:
            audio_player.playback_rate = 1
        else:
            if playing_playlist:
                if current_song_index + 1 < len(playlist_list):
                    current_song_index += 1
                    playsong(None, playlist_list[current_song_index])
            else:
                if current_song_index + 1 < len(library_list):
                    current_song_index += 1
                    playsong(None, library_list[current_song_index])
    
    def play(e):
        nonlocal current_song_index, playlist_list
        current_song_index = 0
        playsong(None, playlist_list[current_song_index])

    def speed_up(e):
        audio_player.playback_rate = 2
    
    def volumechange(e):
        audio_player.volume = e.control.value/100

    def update_edit_fields(e):
        nonlocal current_playlist_id
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Playlists SET name = ?, description = ? WHERE PlaylistID = ?", (edit_playlistNameField.content.value, edit_playlistDescriptionField.content.value, current_playlist_id))
        conn.commit()
    
    def delete_playlist(e):
        nonlocal current_playlist_id
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Song_Playlist WHERE PlaylistID = ?", (current_playlist_id,))
        cursor.execute("DELETE FROM Playlists WHERE PlaylistID = ?", (current_playlist_id,))
        conn.commit()
        editPlaylistScreen(None)
    
    def update_side_playlists():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, PlaylistID FROM Playlists")
        rows = cursor.fetchall()
        conn.close()
        playlistside.controls.clear()
        for row in rows:
            playlistside.controls.append(ft.Container(ft.Text(row[0], style=ft.TextStyle(color=ft.Colors.BLACK), size=20, weight=ft.FontWeight.BOLD), on_click=lambda e, id=row[1]: playlistScreen(e, id)))
        page.update()
    
    def update_row_covers():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT image, PlaylistID FROM Playlists")
        rows = cursor.fetchall()
        conn.close()
        temporary = []
        temporary.append(ft.Container(ft.Image(src=get_asset_path("addPlaylistIcon.png"), fit=ft.ImageFit.FILL), on_click=createPlaylistScreen))
        for row in rows:
            temporary.append(ft.Container(ft.Image(src_base64=row[0], fit=ft.ImageFit.FILL), on_click=lambda e, id=row[1]: playlistScreen(e, id)))
        row_covers.controls = temporary
        page.update()
        
    #? On the Home Screen
    lobbyDesign = ft.Image(src=get_asset_path("music player.png"))
    addplaylistButton = ft.Container(bgcolor="transparent",width=194,height=194,left=262,top=171,padding=10,on_click=createPlaylistScreen) # The + Square at home-screen
    playButton = ft.Container(content=ft.IconButton(icon=ft.Icons.PLAY_ARROW,on_click=musicPlay,icon_color="white"),bgcolor="transparent",left=390,top=13,padding=10,visible=True) # The play button in Home
    shuffleButton = ft.Container(bgcolor="transparent",width=43,height=40,left=265,top=25,padding=10,on_click=shuffle) # The button to shuffle the songs
    rewindButton = ft.Container(bgcolor="transparent",width=30,height=30,left=336,top=27,padding=10,on_click=rewind)
    forwardButton = ft.Container(bgcolor="transparent",width=30,height=30,left=465,top=28,padding=10,on_click=forward, on_long_press=speed_up)
    progress_bar = ft.Container(content=ft.ProgressBar(width=280, value=0, color="white"),bgcolor="transparent",left=510,top=34,padding=10)
    current_song_text = ft.Container(content=ft.Text("", color="black", size=20), top=8, left=520, visible=False)
    volume_slider = ft.Container(content=ft.Slider(min=0, max=100,value=100, on_change=volumechange, width=100,active_color="white"),left=846,top=21)
    row_covers=ft.GridView(controls=[ft.Container(ft.ProgressRing(width=300, height=300, stroke_width=4, color="black"))],height=550, width=725, left=262,top=171, max_extent=225)


    #? sideBarButtons
    homeButton = ft.Container(bgcolor="transparent",width=40,height=40,left=13,top=16,padding=10,on_click=homeScreen) # The Home Icon on the sideBar
    createPlaylistButton = ft.Container(bgcolor="transparent",width=150,height=20,left=20,top=140,padding=10,on_click=createPlaylistScreen) # The button to create the playlist on the home screen
    editPlaylistButton = ft.Container(bgcolor="transparent",width=100,height=20,left=25,top=180,padding=10,on_click=editPlaylistScreen) # The button to edit the playlist on the home screen
    songButton = ft.Container(bgcolor="transparent",width=50,height=20,left=25,top=275,padding=10,on_click=songsScreen) # The songs text in the library
    playlistside = ft.ListView(controls=[], height=360, width=200, left=20, top=360, expand=True, spacing=10)
    

    #? When creating the playlist
    playlistCoverButton = ft.Container(bgcolor="transparent",width=222,height=223,left=366,top=25,padding=10,visible=False,on_click=playlistCoverClicked) # Too add a playlist cover when creating the playlist
    coverImage = ft.Image(src_base64="", width=240,height=240,left=366,top=25, visible=False, fit=ft.ImageFit.FILL) #to add a image
    playlistNameField = ft.Container(content=ft.TextField(color="black",border_color="black"),bgcolor="transparent",left=620,top=95,padding=10,visible=False, ) # The + Square at home-screen
    playlistDescriptionField = ft.Container(content=ft.TextField(color="black",border_color="black"),bgcolor="transparent",left=620,top=200,padding=10,visible=False) # Too add a playlist cover when creating the playlist
    playlistSaveButton = ft.Container(content=ft.ElevatedButton(text="Save Button",on_click=savePlaylist,width=100,bgcolor="black", color="white"),bgcolor="transparent",left=880,top=10,padding=5,visible=False) # temporary save button
    playlistDeleteButton = ft.Container(content=ft.IconButton(on_click=delete_playlist,width=100,bgcolor="Red", icon_color="white", icon=ft.Icons.DELETE),bgcolor="transparent",left=880,top=10,padding=5,visible=False)

    playListSongs = ft.ListView(
        controls=[edit_playlist_songs_table],
        width=568,
        height=190,
        left=360,top=288,visible=False, expand=True
    )


    playlist_display = ft.Row(spacing=10, wrap=True) 

    homeContainer = ft.Container(
        content=ft.Column([
            ft.Container(
                content=playlist_display,
                expand=True,
            )
        ], spacing=10, scroll="auto"), 
        bgcolor="transparent",
        left=450,
        top=150,
        width=600,
        height=400,
        padding=20,
        border_radius=10,
        visible=True
    )

    librarySongs = ft.ListView(controls=[add_songs_table], height=190, width=568, left=360, top=520, expand=True, visible=False)

    #? Playing the Playlist 
    playButtonPlaylist = ft.Container(bgcolor="transparent",width=93,height=55,left=659,top=190,visible=False, on_click=play) 
    shuffleButtonPlaylist = ft.Container(bgcolor="transparent",width=94,height=55,left=808,top=190,visible=False, on_click=shuffle)
    coverImagePlaylist = ft.Image(src_base64="",width=264,height=263,left=360,top=32,visible=False, fit=ft.ImageFit.FILL)
    playlistSongsList = ft.ListView(controls=[playlist_songs_table],width=564,height=390,left=365,top=314,visible=False, expand=True)
    playlistName = ft.Text("",color="black",left=650,top=30,size=30,visible=False)
    playlistDescription = ft.Text("",color="black",left=652,top=90,visible=False)

    #? Editing Playlist
    editPlaylists = ft.ListView(controls=[edit_playlists_table], height=635, width=588, left=340, top=81, expand=True, visible=False)
    edit_playlistNameField = ft.Container(content=ft.TextField(color="black",border_color="black", on_change=update_edit_fields),bgcolor="transparent",left=620,top=95,padding=10,visible=False, )
    edit_playlistDescriptionField = ft.Container(content=ft.TextField(color="black",border_color="black", on_change=update_edit_fields),bgcolor="transparent",left=620,top=200,padding=10,visible=False)


    #? Songs stuff
    songNameField = ft.Container(content=ft.TextField(color="black",border_color="black", hint_text="Enter Song Name:", text_size=20, width=450, cursor_color="black", bgcolor="white", on_change=check_add_change),bgcolor="transparent",left=290,top=85.5,padding=10,visible=False)
    youtubeLinkField = ft.Container(content=ft.TextField(color="black",border_color="black", hint_text="Enter Youtube Link:", text_size=20, width=350, cursor_color="black", bgcolor="white", on_change=check_add_change),bgcolor="transparent",left=570,top=175,padding=10,visible=False)
    currentmusicfile = ""
    filenamedisplay = ft.Container(content=(ft.Text("", color="black")), top=245, left= 300)
    addsongButton = ft.Container(bgcolor="transparent",width=158,height=51,left=782,top=97,padding=10,on_click= lambda e: addSongClicked(e, currentmusicfile), visible=False)
    addsongfile = ft.Container(bgcolor="transparent",width=155,height=51,left=298,top=187,padding=10,on_click=lambda e: addSongFileClicked(e,page), visible=False, on_tap_down=check_add_change)

    designStack = ft.Stack([lobbyDesign,createPlaylistButton,editPlaylistButton,addplaylistButton,songButton,
    coverImage,playlistNameField,playlistDescriptionField,playlistSaveButton,playButton, playlistCoverButton,
    progress_bar,homeButton,shuffleButton,rewindButton,forwardButton,playButtonPlaylist,shuffleButtonPlaylist,
    coverImagePlaylist, songs_scrollable_table ,playlistSongsList,playListSongs,librarySongs,audio_player,
    songNameField, youtubeLinkField, addsongButton, addsongfile, homeContainer, filenamedisplay, current_song_text, volume_slider,
    editPlaylists, playlistDeleteButton, playlistside, playlistName, playlistDescription, row_covers, edit_playlistNameField,
    edit_playlistDescriptionField])
    
    page.add(designStack)
    update_side_playlists()
    update_row_covers()
    page.update()

ft.app(target=main)
