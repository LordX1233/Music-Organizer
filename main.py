import flet as ft
import base64
import os

import sys

def get_asset_path(filename):
    if getattr(sys, 'frozen', False):
        base_path = os.path.join(sys._MEIPASS, "assets")
    else: base_path = ""
    return os.path.join(base_path, filename)

def main(page: ft.Page):
    # audio_player = None  # To store the audio control
    page.theme_mode = ft.ThemeMode.DARK
    page.title = 'Music Organizer'
    page.window.width = 1024
    page.window.height = 768
    # page.scroll = True
    page.window.resizable = False

    songs_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Song name", style=ft.TextStyle(color=ft.colors.WHITE), width=490)),
            ft.DataColumn(ft.Text("Delete", style=ft.TextStyle(color=ft.colors.WHITE))),
        ],
        left=300,
        top=275,
        heading_row_color="black",
        visible=False
    )

    def songs_table_load():
        songs_table.rows.clear()
        for root, dirs, files in os.walk("Songs"):
            for file in files:
                file_name, _ = os.path.splitext(file) 
                songs_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(file_name, style=ft.TextStyle(color=ft.colors.BLUE))), 
                        ft.DataCell(ft.Text("Delete", style=ft.TextStyle(color=ft.colors.BLUE))),
                    ])
                )
        page.update()
    
    songs_table_load()


    def fetch_list_of_songs():
        pass

    def make_everything_invisible():
        coverImagePlaylist.visible = playlistSongsList.visible = playListSongs.visible = librarySongs.visible = songs_table.visible = PauseButton.visible = coverImage.visible = addplaylistButton.visible = playButton.visible = slider.visible = rewindButton.visible = forwardButton.visible = shuffleButton.visible = playButtonPlaylist.visible = shuffleButtonPlaylist.visible = songsQuantity.visible = playlistCoverButton.visible = playlistNameButton.visible = playlistDescriptionButton.visible = playlistSaveButton.visible = False
        page.update()
    
    def homeScreen(e):
        lobbyDesign.src=get_asset_path("music player.png")
        make_everything_invisible()
        addplaylistButton.visible = playButton.visible = slider.visible = rewindButton.visible = forwardButton.visible = shuffleButton.visible = True
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
        page.update()

    def editPlaylistScreen():
        lobbyDesign.src = get_asset_path("editPlaylist.png")
        make_everything_invisible()
        playlistCoverButton.visible = playlistNameButton.visible = playlistDescriptionButton.visible = playlistSaveButton.visible = playListSongs.visible = librarySongs.visible = True
        page.update()

    # def createPlaylistClicked(e):
    #     page.update()
        

    def editPlaylistClicked(e):
        print("edit playlistClicked")
        pass

    def addSongClicked(e):
        print("Songs clicked")
        pass

    def songsClicked(e):
        lobbyDesign.src=get_asset_path("songsScreen.png")
        make_everything_invisible()
        songs_table.visible = True
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

    # def saveClicked(e):
    #     homeScreen()  
    #     page.update()
    
    def musicPlay(e):
        playButton.visible = False
        PauseButton.visible = True
        page.update()
        pass

    def musicPause(e):
        playButton.visible = True
        PauseButton.visible = False
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
    PauseButton = ft.Container(content=ft.IconButton(icon=ft.icons.PAUSE_SHARP,on_click=musicPause,icon_color="white"),bgcolor="transparent",left=384,top=13,padding=10,visible=False) # The pause button in Home
    shuffleButton = ft.Container(bgcolor="transparent",width=43,height=40,left=265,top=25,padding=10,on_click=shuffle) # The button to shuffle the songs
    rewindButton = ft.Container(bgcolor="transparent",width=30,height=30,left=336,top=27,padding=10,on_click=rewind)
    forwardButton = ft.Container(bgcolor="transparent",width=30,height=30,left=465,top=28,padding=10,on_click=forward)
    slider = ft.Container(content=ft.Slider(min=0, max=100, label="{value}%",width=335),bgcolor="transparent",left=570,top=12,padding=10)


    #? sideBarButtons
    homeButton = ft.Container(bgcolor="transparent",width=40,height=40,left=13,top=16,padding=10,on_click=homeScreen) # The Home Icon on the sideBar
    createPlaylistButton = ft.Container(bgcolor="transparent",width=150,height=20,left=20,top=140,padding=10,on_click=createPlaylistScreen) # The button to create the playlist on the home screen
    editPlaylistButton = ft.Container(bgcolor="transparent",width=100,height=20,left=25,top=180,padding=10,on_click=editPlaylistClicked) # The button to edit the playlist on the home screen
    songButton = ft.Container(bgcolor="transparent",width=50,height=20,left=25,top=275,padding=10,on_click=songsClicked) # The songs text in the library
    

    #? When creating the playlist
    playlistCoverButton = ft.Container(bgcolor="transparent",width=222,height=223,left=366,top=25,padding=10,visible=False,on_click=lambda e: playlistCoverClicked(e, page, playlistCoverButton, coverImage)) # Too add a playlist cover when creating the playlist
    coverImage = ft.Image(src="", width=240,height=240,left=366,top=25, visible=False, fit=ft.ImageFit.COVER) #to add a image
    playlistNameButton = ft.Container(content=ft.TextField(color="black",border_color="black"),bgcolor="transparent",left=620,top=95,padding=10,visible=False) # The + Square at home-screen
    playlistDescriptionButton = ft.Container(content=ft.TextField(color="black",border_color="black"),bgcolor="transparent",left=620,top=200,padding=10,visible=False) # Too add a playlist cover when creating the playlist
    playlistSaveButton = ft.Container(content=ft.ElevatedButton(text="Save Button",on_click=homeScreen,width=400,bgcolor="black", color="white"),bgcolor="transparent",left=480,top=655,padding=10,visible=False) # temporary save button
    playListSongs = ft.Container(width=600,height=170,bgcolor="#E9E8E7",left=330,top=290,padding=10,visible=False)
    librarySongs = ft.Container(width=600,height=170,bgcolor="#E9E8E7",left=330,top=480,padding=10,visible=False)

    #? Playing the Playlist 
    playButtonPlaylist = ft.Container(bgcolor="transparent",width=95,height=55,left=645,top=185,padding=10,visible=False) 
    shuffleButtonPlaylist = ft.Container(bgcolor="transparent",width=95,height=55,left=795,top=185,padding=10,visible=False)
    coverImagePlaylist = ft.Container(bgcolor="transparent",width=260,height=258,left=357,top=33,padding=10,visible=False)
    songsQuantity = ft.Container(content=ft.Text("Number of songs in playlist"),width=95,height=55,left=740,top=265,visible=True)
    playlistSongsList = ft.Container(bgcolor="#E9E8E7",width=579,height=390,left=355,top=314,visible=False)

    designStack = ft.Stack([lobbyDesign,createPlaylistButton,editPlaylistButton,addplaylistButton,songButton,
    playlistCoverButton,coverImage,playlistNameButton,playlistDescriptionButton,playlistSaveButton,playButton,
    PauseButton,slider,homeButton,shuffleButton,rewindButton,forwardButton,playButtonPlaylist,shuffleButtonPlaylist,
    coverImagePlaylist,songsQuantity, songs_table,playlistSongsList,playListSongs,librarySongs])
    
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
