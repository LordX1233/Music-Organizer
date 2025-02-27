import sqlite3
import flet as ft
import base64
import os

import sys

playlists = []
selected_image_path = None 

def get_asset_path(filename, subfolder="assets"):
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

    def playsong(e, song):
        nonlocal playing
        audio_player.src = get_asset_path(song, subfolder="songs")
        playButton.content.icon = ft.icons.PAUSE_SHARP
        playing = True
        audio_player.play()
        page.update()
    
    def delete_song(e, song):
        print(song)
        os.remove(get_asset_path(song, subfolder="songs"))
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
                        ft.DataCell(ft.Icon(ft.icons.ADD_CIRCLE, color=ft.colors.GREEN)),
                    ])
                )
        page.update()

    def songs_table_load():
        songs_table.rows.clear()
        for root, dirs, files in os.walk("Songs"):
            for file in files:
                file_name, _ = os.path.splitext(file) 
                songs_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(file_name, style=ft.TextStyle(color=ft.colors.BLACK)), on_tap=lambda e, f=file: playsong(e, f)), 
                        ft.DataCell(ft.Icon(ft.icons.DELETE, color=ft.colors.RED), on_tap=lambda e, f=file: delete_song(e, f)),
                    ])
                )
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
        coverImagePlaylist.visible = playlistSongsList.visible = playListSongs.visible = librarySongs.visible = songs_scrollable_table.visible = coverImage.visible = addplaylistButton.visible = playButton.visible = slider.visible = rewindButton.visible = forwardButton.visible = shuffleButton.visible = playButtonPlaylist.visible = shuffleButtonPlaylist.visible = songsQuantity.visible = playlistCoverButton.visible = playlistNameButton.visible = playlistDescriptionButton.visible = playlistSaveButton.visible = homeContainer.visible = False
        page.update()
    
    def homeScreen(e=None):
        lobbyDesign.src=get_asset_path("music player.png")
        make_everything_invisible()
        addplaylistButton.visible = playButton.visible = slider.visible = rewindButton.visible = forwardButton.visible = shuffleButton.visible= homeContainer.visible = True
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
        playlistCoverButton.visible = playlistNameButton.visible = playlistDescriptionButton.visible = playlistSaveButton.visible = playListSongs.visible = librarySongs.visible = True
        add_songs_table_load()
        page.update()

    def editPlaylistScreen(e):
        lobbyDesign.src = get_asset_path("editPlaylist.png")
        make_everything_invisible()
        playlistCoverButton.visible = playlistNameButton.visible = playlistDescriptionButton.visible = playlistSaveButton.visible = playListSongs.visible = librarySongs.visible = True
        add_songs_table_load()
        page.update()

        #! para guardar el paylist
    def savePlaylist(e):
        global selected_image_path
        print(f"Name: {playlistNameButton.content.value}")
        print(f"Description: {playlistDescriptionButton.content.value}")
        print(f"Image Path: {selected_image_path}")

        if playlistNameButton.content.value and playlistDescriptionButton.content.value and selected_image_path:
            playlists.append({
                "name": playlistNameButton.content.value,
                "description": playlistDescriptionButton.content.value,
                "cover": selected_image_path
            })
            homeScreen(None)

        

    def editPlaylistClicked(e):
        print("edit playlistClicked")
        pass

    def addSongClicked(e):
        print("Songs clicked")
        pass

    def songsClicked(e):
        lobbyDesign.src=get_asset_path("songsScreen.png")
        make_everything_invisible()
        songs_scrollable_table.visible = True
        songs_table_load()
        page.update()

    def playlistCoverClicked(e, page, playlistCoverButton, coverImage):
        print("choose the album cover")
        
        def fileSelected(e: ft.FilePickerResultEvent):
            if e.files:
                file = e.files[0]
                playlistCoverButton.visible = False
                coverImage.src = file.path
                coverImage.visible = True
            page.update()

        filePicker = ft.FilePicker(on_result=fileSelected)
        page.overlay.append(filePicker)
        page.update() 

        filePicker.pick_files(allow_multiple=False, allowed_extensions=["jpg", "png", "jpeg"])

    def musicPlay(e):
        nonlocal playing
        if playing:
            playButton.content.icon = ft.icons.PLAY_ARROW
            playing = False
            audio_player.pause()
        else:
            playButton.content.icon = ft.icons.PAUSE_SHARP
            playing = True
            audio_player.resume()
        page.update()
        pass

    def shuffle(e):
        page.update()
        pass

    def rewind(e):
        page.update()
        pass

    def forward(e):
        page.update()
        pass
        
    #? On the Home Screen
    lobbyDesign = ft.Image(src=get_asset_path("music player.png"))
    addplaylistButton = ft.Container(bgcolor="transparent",width=200,height=193,left=257,top=167,padding=10,on_click=createPlaylistScreen) # The + Square at home-screen
    playButton = ft.Container(content=ft.IconButton(icon=ft.icons.PLAY_ARROW,on_click=musicPlay,icon_color="white"),bgcolor="transparent",left=384,top=13,padding=10,visible=True) # The play button in Home
    shuffleButton = ft.Container(bgcolor="transparent",width=43,height=40,left=265,top=25,padding=10,on_click=shuffle) # The button to shuffle the songs
    rewindButton = ft.Container(bgcolor="transparent",width=30,height=30,left=336,top=27,padding=10,on_click=rewind)
    forwardButton = ft.Container(bgcolor="transparent",width=30,height=30,left=465,top=28,padding=10,on_click=forward)
    slider = ft.Container(content=ft.Slider(min=0, max=100, label="{value}%",width=335),bgcolor="transparent",left=570,top=12,padding=10)


    #? sideBarButtons
    homeButton = ft.Container(bgcolor="transparent",width=40,height=40,left=13,top=16,padding=10,on_click=homeScreen) # The Home Icon on the sideBar
    createPlaylistButton = ft.Container(bgcolor="transparent",width=150,height=20,left=20,top=140,padding=10,on_click=createPlaylistScreen) # The button to create the playlist on the home screen
    editPlaylistButton = ft.Container(bgcolor="transparent",width=100,height=20,left=25,top=180,padding=10,on_click=editPlaylistScreen) # The button to edit the playlist on the home screen
    songButton = ft.Container(bgcolor="transparent",width=50,height=20,left=25,top=275,padding=10,on_click=songsClicked) # The songs text in the library
    

    #? When creating the playlist
    playlistCoverButton = ft.Container(bgcolor="transparent",width=222,height=223,left=366,top=25,padding=10,visible=False,on_click=lambda e: playlistCoverClicked(e, page, playlistCoverButton, coverImage)) # Too add a playlist cover when creating the playlist
    coverImage = ft.Image(src="", width=240,height=240,left=366,top=25, visible=False, fit=ft.ImageFit.COVER) #to add a image
    playlistNameButton = ft.Container(content=ft.TextField(color="black",border_color="black"),bgcolor="transparent",left=620,top=95,padding=10,visible=False) # The + Square at home-screen
    playlistDescriptionButton = ft.Container(content=ft.TextField(color="black",border_color="black"),bgcolor="transparent",left=620,top=200,padding=10,visible=False) # Too add a playlist cover when creating the playlist
    playlistSaveButton = ft.Container(content=ft.ElevatedButton(text="Save Button",on_click=savePlaylist,width=400,bgcolor="black", color="white"),bgcolor="transparent",left=480,top=30,padding=10,visible=False) # temporary save button
    playListSongs = ft.Container(width=600,height=170,bgcolor="#E9E8E7",left=330,top=290,padding=10,visible=False)
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

    librarySongs = ft.ListView(
        controls=[add_songs_table],
        height=190,
        width=568,
        left=360,
        top=520,
        expand=True,
        visible=False
    )

    #? Playing the Playlist 
    playButtonPlaylist = ft.Container(bgcolor="transparent",width=95,height=55,left=645,top=185,padding=10,visible=False) 
    shuffleButtonPlaylist = ft.Container(bgcolor="transparent",width=95,height=55,left=795,top=185,padding=10,visible=False)
    coverImagePlaylist = ft.Container(bgcolor="transparent",width=260,height=258,left=357,top=33,padding=10,visible=False)
    songsQuantity = ft.Container(content=ft.Text("Number of songs in playlist"),width=95,height=55,left=740,top=265,visible=True)
    playlistSongsList = ft.Container(bgcolor="#E9E8E7",width=579,height=390,left=355,top=314,visible=False)

    designStack = ft.Stack([lobbyDesign,createPlaylistButton,editPlaylistButton,addplaylistButton,songButton,
    playlistCoverButton,coverImage,playlistNameButton,playlistDescriptionButton,playlistSaveButton,playButton,
    slider,homeButton,shuffleButton,rewindButton,forwardButton,playButtonPlaylist,shuffleButtonPlaylist,
    coverImagePlaylist,songsQuantity, songs_scrollable_table ,playlistSongsList,playListSongs,librarySongs,audio_player])
    
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
