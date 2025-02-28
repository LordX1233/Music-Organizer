import sqlite3
import flet as ft
import base64
import os
from pytubefix import YouTube
import shutil
import sys


import asyncio

playlists = []
selected_image_path = None  
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

    audio_player = ft.Audio(src=" ", autoplay=True)
    library_list = []
    current_song_index = 0

    def playsong(e, song):
        nonlocal playing, current_song_index
        audio_player.src = get_asset_path(song, subfolder="Songs")
        playButton.content.icon = ft.Icons.PAUSE_SHARP
        playing = True
        audio_player.play()
        current_song_index = library_list.index(song)
        current_song_text.content.value = os.path.splitext(song)[0]
        audio_player.on_ended = lambda e: forward(e)
        audio_player.on_position_changed = lambda e: update_progress()
        page.update()
    
    def delete_song(e, song):
        print(song)
        os.remove(get_asset_path(song, subfolder="Songs"))
        songs_table_load()
        pass
        
    songs_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Song name", style=ft.TextStyle(color=ft.colors.WHITE), width=490)),
            ft.DataColumn(ft.Text("Delete", style=ft.TextStyle(color=ft.colors.WHITE))),
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

    def add_songs_table_load():
        add_songs_table.rows.clear()
        for root, dirs, files in os.walk("Songs"):
            for file in files:
                file_name, _ = os.path.splitext(file) 
                add_songs_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(file_name, style=ft.TextStyle(color=ft.colors.BLACK)), on_tap=lambda e, f=file: playsong(e, f)), 
                        ft.DataCell(ft.IconButton(ft.Icons.ADD_CIRCLE, icon_color=ft.colors.GREEN, on_click=add_song_to_playlist)),
                    ])
                )
        page.update()
    
    def add_song_to_playlist(e, song):
        playlist_songs_table.rows.append(
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(song, style=ft.TextStyle(color=ft.colors.BLACK))),
                ft.DataCell(ft.Icon(ft.Icons.DELETE, color=ft.colors.RED, on_click=lambda e, f=song: remove_song_from_playlist(e, f))),
            ])
        )
        page.update()
    
    def remove_song_from_playlist(e, song):
        for row in playlist_songs_table.rows:
            if row.cells[0].content == song:
                playlist_songs_table.rows.remove(row)
                break
        page.update()
    
    playlist_songs_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Song name", style=ft.TextStyle(color=ft.colors.WHITE), width=440)),
            ft.DataColumn(ft.Text("Delete", style=ft.TextStyle(color=ft.colors.WHITE))),
        ],
        heading_row_color="black",
    )

            
    def songs_table_load():
        songs_table.rows.clear()
        library_list.clear()
        for root, dirs, files in os.walk("Songs"):
            for file in files:
                file_name, _ = os.path.splitext(file) 
                songs_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(file_name, style=ft.TextStyle(color=ft.colors.BLACK)), on_tap=lambda e, f=file: playsong(e, f)), 
                        ft.DataCell(ft.Icon(ft.Icons.DELETE, color=ft.colors.RED), on_tap=lambda e, f=file: delete_song(e, f)),
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


    def fetch_list_of_songs():
        pass

    def make_everything_invisible():
        current_song_text.visible = filenamedisplay.visible = addsongfile.visible = addsongButton.visible = youtubeLinkField.visible = songNameField.visible = coverImagePlaylist.visible = playlistSongsList.visible = playListSongs.visible = librarySongs.visible = songs_scrollable_table.visible = coverImage.visible = addplaylistButton.visible = playButton.visible = progress_bar.visible = rewindButton.visible = forwardButton.visible = shuffleButton.visible = playButtonPlaylist.visible = shuffleButtonPlaylist.visible = songsQuantity.visible = playlistCoverButton.visible = playlistNameButton.visible = playlistDescriptionField.visible = playlistSaveButton.visible = homeContainer.visible = False
        page.update()
    
    def homeScreen(e=None):
        lobbyDesign.src=get_asset_path("music player.png")
        make_everything_invisible()
        current_song_text.visible = addplaylistButton.visible = playButton.visible = progress_bar.visible = rewindButton.visible = forwardButton.visible = shuffleButton.visible= homeContainer.visible = True
        page.update()
        playlist_display.controls.clear()
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

    def playlistScreen(e):
        lobbyDesign.src=get_asset_path("playlistScreen.png")
        make_everything_invisible()
        playButtonPlaylist.visible = shuffleButtonPlaylist.visible = coverImagePlaylist.visible = songsQuantity.visible = playlistSongsList.visible = True
        
        page.update()

    def createPlaylistScreen(e):
        lobbyDesign.src=get_asset_path("createPlaylist.png")
        make_everything_invisible()
        playlistCoverButton.visible = playlistNameButton.visible = playlistDescriptionField.visible = playlistSaveButton.visible = playListSongs.visible = librarySongs.visible = True
        add_songs_table_load()
        page.update()

    def editPlaylistScreen(e):
        lobbyDesign.src = get_asset_path("editPlaylist.png")
        make_everything_invisible()
        playlistCoverButton.visible = playlistNameButton.visible = playlistDescriptionField.visible = playlistSaveButton.visible = playListSongs.visible = librarySongs.visible = True
        add_songs_table_load()
        page.update()

        #! para guardar el paylist
    def savePlaylist(e):
        global selected_image_path
        print(f"Name: {playlistNameButton.content.value}")
        print(f"Description: {playlistDescriptionField.content.value}")
        print(f"Image Path: {selected_image_path}")

        if playlistNameButton.content.value and playlistDescriptionField.content.value and selected_image_path:
            playlists.append({
                "name": playlistNameButton.content.value,
                "description": playlistDescriptionField.content.value,
                "cover": selected_image_path
            })
            homeScreen(None)

        

    def editPlaylistClicked(e):
        print("edit playlistClicked")
        pass

    def addSongClicked(e, currentmusicfile):
        if youtubeLinkField.content.value == "":
            file_path = currentmusicfile
            print(currentmusicfile)
            file_extension = os.path.splitext(file_path)[1]
            new_file_name = f"{ songNameField.content.value}{file_extension}"  # Rename using song_name
            destination = os.path.join("Songs", new_file_name)  # Define new path
            shutil.copy(file_path, destination)
        else:
            yt = YouTube(youtubeLinkField.content.value)
            audio_stream = yt.streams.filter(only_audio=True).first()
            os.makedirs("Songs", exist_ok=True)
            audio_file = audio_stream.download(output_path="Songs")
            mp3_file = os.path.join("Songs", songNameField.content.value + ".mp3")
            os.rename(audio_file, mp3_file)
        songs_table_load()
        page.update
    
    def songsScreen(e):
        lobbyDesign.src=get_asset_path("songsScreen.png")
        make_everything_invisible()
        filenamedisplay.visible = addsongfile.visible = songs_scrollable_table.visible = songNameField.visible = youtubeLinkField.visible = True
        songs_table_load()
        page.update()
    
    def addSongFileClicked(e, page): 
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
        print(library_list)
        if songNameField.content.value != "" and (youtubeLinkField.content.value != "" or currentmusicfile != ""):
            addsongButton.visible = True
        else:
            addsongButton.visible = False
        page.update()



    def playlistCoverClicked(e, page, playlistCoverButton, coverImage):
        print("choose the album cover")

        def fileSelected(e: ft.FilePickerResultEvent):
            global selected_image_path  
            if e.files:
                file = e.files[0]
                selected_image_path = file.path  
                playlistCoverButton.visible = False
                coverImage.src = selected_image_path
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
        page.update()
        pass

    def rewind(e):
        nonlocal current_song_index 
        if audio_player.get_current_position() >= audio_player.get_duration()/2:
            playsong(None, library_list[current_song_index])
        else:
            if current_song_index - 1 != -1:
                current_song_index -= 1
                playsong(None, library_list[current_song_index])
            else:
                playsong(None, library_list[current_song_index])
            
        
    def forward(e):
        nonlocal current_song_index
        if current_song_index + 1 < len(library_list):
            current_song_index += 1
            playsong(None, library_list[current_song_index])
    
        
    #? On the Home Screen
    lobbyDesign = ft.Image(src=get_asset_path("music player.png"))
    addplaylistButton = ft.Container(bgcolor="transparent",width=200,height=193,left=257,top=167,padding=10,on_click=createPlaylistScreen) # The + Square at home-screen
    playButton = ft.Container(content=ft.IconButton(icon=ft.Icons.PLAY_ARROW,on_click=musicPlay,icon_color="white"),bgcolor="transparent",left=384,top=13,padding=10,visible=True) # The play button in Home
    shuffleButton = ft.Container(bgcolor="transparent",width=43,height=40,left=265,top=25,padding=10,on_click=shuffle) # The button to shuffle the songs
    rewindButton = ft.Container(bgcolor="transparent",width=30,height=30,left=336,top=27,padding=10,on_click=rewind)
    forwardButton = ft.Container(bgcolor="transparent",width=30,height=30,left=465,top=28,padding=10,on_click=forward)
    progress_bar = ft.Container(content=ft.ProgressBar(width=335, value=0, color="white"),bgcolor="transparent",left=582,top=34,padding=10)
    current_song_text = ft.Container(content=ft.Text("", color="black", size=20), top=8, left=610, visible=False)


    #? sideBarButtons
    homeButton = ft.Container(bgcolor="transparent",width=40,height=40,left=13,top=16,padding=10,on_click=homeScreen) # The Home Icon on the sideBar
    createPlaylistButton = ft.Container(bgcolor="transparent",width=150,height=20,left=20,top=140,padding=10,on_click=createPlaylistScreen) # The button to create the playlist on the home screen
    editPlaylistButton = ft.Container(bgcolor="transparent",width=100,height=20,left=25,top=180,padding=10,on_click=editPlaylistScreen) # The button to edit the playlist on the home screen
    songButton = ft.Container(bgcolor="transparent",width=50,height=20,left=25,top=275,padding=10,on_click=songsScreen) # The songs text in the library
    

    #? When creating the playlist
    playlistCoverButton = ft.Container(bgcolor="transparent",width=222,height=223,left=366,top=25,padding=10,visible=False,on_click=lambda e: playlistCoverClicked(e, page, playlistCoverButton, coverImage)) # Too add a playlist cover when creating the playlist
    coverImage = ft.Image(src="", width=240,height=240,left=366,top=25, visible=False, fit=ft.ImageFit.COVER) #to add a image
    playlistNameButton = ft.Container(content=ft.TextField(color="black",border_color="black"),bgcolor="transparent",left=620,top=95,padding=10,visible=False) # The + Square at home-screen
    playlistDescriptionField = ft.Container(content=ft.TextField(color="black",border_color="black"),bgcolor="transparent",left=620,top=200,padding=10,visible=False) # Too add a playlist cover when creating the playlist
    playlistSaveButton = ft.Container(content=ft.ElevatedButton(text="Save Button",on_click=savePlaylist,width=400,bgcolor="black", color="white"),bgcolor="transparent",left=480,top=30,padding=5,visible=False) # temporary save button
    
    playListSongs = ft.Container(
        content=ft.Column([playlist_songs_table], spacing=10),
        bgcolor="#E9E8E7",
        width=590,
        height=200,
        left=340,top=290,padding=10,visible=False
    )
    # librarySongs = ft.Container(width=600,height=170,bgcolor="#E9E8E7",left=330,top=480,padding=10,visible=False)

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
    playButtonPlaylist = ft.Container(bgcolor="transparent",width=95,height=55,left=645,top=185,padding=10,visible=False) 
    shuffleButtonPlaylist = ft.Container(bgcolor="transparent",width=95,height=55,left=795,top=185,padding=10,visible=False)
    coverImagePlaylist = ft.Container(bgcolor="transparent",width=260,height=258,left=357,top=33,padding=10,visible=False)
    songsQuantity = ft.Container(content=ft.Text("Number of songs in playlist"),width=95,height=55,left=740,top=265,visible=True)
    playlistSongsList = ft.Container(bgcolor="#E9E8E7",width=579,height=390,left=355,top=314,visible=False)


    #? Songs stuff
    songNameField = ft.Container(content=ft.TextField(color="black",border_color="black", hint_text="Enter Song Name:", text_size=20, width=450, cursor_color="black", bgcolor="white", on_change=check_add_change),bgcolor="transparent",left=290,top=85.5,padding=10,visible=False)
    youtubeLinkField = ft.Container(content=ft.TextField(color="black",border_color="black", hint_text="Enter Youtube Link:", text_size=20, width=350, cursor_color="black", bgcolor="white", on_change=check_add_change),bgcolor="transparent",left=570,top=175,padding=10,visible=False)
    currentmusicfile = ""
    filenamedisplay = ft.Container(content=(ft.Text("", color="black")), top=245, left= 300)
    addsongButton = ft.Container(bgcolor="transparent",width=158,height=51,left=782,top=97,padding=10,on_click= lambda e: addSongClicked(e, currentmusicfile), visible=False)
    addsongfile = ft.Container(bgcolor="transparent",width=155,height=51,left=298,top=187,padding=10,on_click=lambda e: addSongFileClicked(e,page), visible=False, on_tap_down=check_add_change)

    designStack = ft.Stack([lobbyDesign,createPlaylistButton,editPlaylistButton,addplaylistButton,songButton,
    playlistCoverButton,coverImage,playlistNameButton,playlistDescriptionField,playlistSaveButton,playButton,
    progress_bar,homeButton,shuffleButton,rewindButton,forwardButton,playButtonPlaylist,shuffleButtonPlaylist,
    coverImagePlaylist,songsQuantity, songs_scrollable_table ,playlistSongsList,playListSongs,librarySongs,audio_player,
    songNameField, youtubeLinkField, addsongButton, addsongfile, homeContainer, filenamedisplay, current_song_text])
    
    page.add(designStack)
    page.update()


    #? file_picker = ft.FilePicker(on_result=on_file_selected)
    #? page.overlay.append(file_picker)

    # Add a button to trigger file picking
    #? page.add(
    #?     ft.ElevatedButton(
    #?         "Pick a music file",
    #?         on_click=lambda e: file_picker.pick_files(allow_multiple=False),
    #?     )
    #? )

ft.app(target=main)

