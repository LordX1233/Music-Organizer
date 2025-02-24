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

    def homeScreen():
        lobbyDesing.src=get_asset_path("music player.png")
        playlistCoverButton.visible = False
        playlistNameButton.visible = False
        playlistDescriptionButton.visible = False
        playlistSaveButton.visible = False
        addSongButton.visible = True
        playButton.visible = True
        slider.visible = True
        rewindButton.visible = True
        forwardButton.visible = True
        shuffleButton.visible = True
        playButtonPlaylist.visible = False
        shuffleButtonPlaylist.visible = False
        coverImagePlaylist.visible = False
        songsQuantity.visible = False
        coverImage.visible = False
        page.update()

    def playlistScreen():
        lobbyDesing.src=get_asset_path("playlistScreen.png")
        playButtonPlaylist.visible = True
        shuffleButtonPlaylist.visible = True
        coverImagePlaylist.visible = True
        songsQuantity.visible = True
        playlistCoverButton.visible = False
        playlistNameButton.visible = False
        playlistDescriptionButton.visible = False
        playlistSaveButton.visible = False
        addSongButton.visible = False
        playButton.visible = False
        PauseButton.visible = False
        slider.visible = False
        rewindButton.visible = False
        forwardButton.visible = False
        shuffleButton.visible = False
        coverImage.visible = False
        page.update()

    def createPlaylistScreen():
        lobbyDesing.src=get_asset_path("createPlaylist.png")
        playlistCoverButton.visible = True
        playlistNameButton.visible = True
        playlistDescriptionButton.visible = True
        playlistSaveButton.visible = True
        addSongButton.visible = False
        playButton.visible = False
        PauseButton.visible = False
        slider.visible = False
        rewindButton.visible = False
        forwardButton.visible = False
        shuffleButton.visible = False
        playButtonPlaylist.visible = False
        shuffleButtonPlaylist.visible = False
        coverImagePlaylist.visible = False
        songsQuantity.visible = False
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
        print("Add button clicked")
        pass

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
    lobbyDesing = ft.Image(src=get_asset_path("music player.png"))
    addSongButton = ft.Container(bgcolor="transparent",width=200,height=193,left=257,top=167,padding=10,on_click=songsClicked) # The + Square at home-screen
    playButton = ft.Container(content=ft.IconButton(icon=ft.icons.PLAY_ARROW,on_click=musicPlay,icon_color="white"),bgcolor="transparent",left=384,top=13,padding=10,visible=True) # The play button in Home
    PauseButton = ft.Container(content=ft.IconButton(icon=ft.icons.PAUSE_SHARP,on_click=musicPause,icon_color="white"),bgcolor="transparent",left=384,top=13,padding=10,visible=False) # The pause button in Home
    shuffleButton = ft.Container(bgcolor="transparent",width=43,height=40,left=265,top=25,padding=10,on_click=shuffle) # The button to shuffle the songs
    rewindButton = ft.Container(bgcolor="transparent",width=30,height=30,left=336,top=27,padding=10,on_click=rewind)
    forwardButton = ft.Container(bgcolor="transparent",width=30,height=30,left=465,top=28,padding=10,on_click=forward)
    slider = ft.Container(content=ft.Slider(min=0, max=100, label="{value}%",width=335),bgcolor="transparent",left=570,top=12,padding=10)


    #? sideBarButtons
    homeButton = ft.Container(bgcolor="transparent",width=40,height=40,left=13,top=16,padding=10,on_click= lambda _: homeScreen()) # The Home Icon on the sideBar
    createPlaylistButton = ft.Container(bgcolor="transparent",width=150,height=20,left=20,top=140,padding=10,on_click= lambda _: createPlaylistScreen()) # The button to create the playlist on the home screen
    editPlaylistButton = ft.Container(bgcolor="transparent",width=100,height=20,left=25,top=180,padding=10,on_click=editPlaylistClicked) # The button to edit the playlist on the home screen
    songButton = ft.Container(bgcolor="transparent",width=50,height=20,left=25,top=275,padding=10,on_click= lambda _: playlistScreen()) # The songs text in the library
    

    #? When creating the playlist
    playlistCoverButton = ft.Container(bgcolor="transparent",width=222,height=223,left=366,top=25,padding=10,visible=False,on_click=lambda e: playlistCoverClicked(e, page, playlistCoverButton, coverImage)) # Too add a playlist cover when creating the playlist
    coverImage = ft.Image(src="", width=240,height=240,left=366,top=25, visible=False, fit=ft.ImageFit.COVER) #to add a image
    playlistNameButton = ft.Container(content=ft.TextField(color="black",border_color="black"),bgcolor="transparent",left=620,top=95,padding=10,visible=False) # The + Square at home-screen
    playlistDescriptionButton = ft.Container(content=ft.TextField(color="black",border_color="black"),bgcolor="transparent",left=620,top=200,padding=10,visible=False) # Too add a playlist cover when creating the playlist
    playlistSaveButton = ft.Container(content=ft.ElevatedButton(text="Save Button",on_click= lambda _: homeScreen(),width=400,bgcolor="black", color="white"),bgcolor="transparent",left=480,top=655,padding=10,visible=False) # temporary save button

    #? Playing the Playlist
    playButtonPlaylist = ft.Container(bgcolor="transparent",width=95,height=55,left=645,top=185,padding=10,visible=False) 
    shuffleButtonPlaylist = ft.Container(bgcolor="transparent",width=95,height=55,left=795,top=185,padding=10,visible=False)
    coverImagePlaylist = ft.Container(bgcolor="transparent",width=260,height=258,left=357,top=33,padding=10,visible=False)
    songsQuantity = ft.Container(content=ft.Text("Number of songs in playlist"),width=95,height=55,left=740,top=265,visible=True)

    designStack = ft.Stack([lobbyDesing,createPlaylistButton,editPlaylistButton,addSongButton,songButton,playlistCoverButton,coverImage,playlistNameButton,playlistDescriptionButton,playlistSaveButton,playButton,PauseButton,slider,homeButton,shuffleButton,rewindButton,forwardButton,playButtonPlaylist,shuffleButtonPlaylist,coverImagePlaylist,songsQuantity])
    
    page.add(designStack)
    page.update()



    
    # def on_file_selected(e: ft.FilePickerResultEvent):
    #     nonlocal audio_player
    #     if e.files:
    #         # Allowed music file extensions
    #         allowed_extensions = {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"}
    #         file = e.files[0]
            
    #         # Validate the file extension
    #         if not any(file.name.lower().endswith(ext) for ext in allowed_extensions):
    #             page.add(ft.Text("Invalid file type! Please select a music file."))
    #             page.update()
    #             return

    #         # Try to get file bytes if available, otherwise read from file.path
    #         file_data = None
    #         if hasattr(file, "bytes"):
    #             file_data = file.bytes

    #         if file_data is None and file.path:
    #             try:
    #                 with open(file.path, "rb") as f:
    #                     file_data = f.read()
    #             except Exception as ex:
    #                 page.add(ft.Text(f"Error reading file: {ex}"))
    #                 page.update()
    #                 return

    #         if file_data is not None:
    #             # Convert the file data to a base64 string and create a data URL
    #             base64_data = base64.b64encode(file_data).decode("utf-8")
    #             ext = file.name.lower().rsplit(".", 1)[-1]
    #             mime = {
    #                 "mp3": "audio/mpeg",
    #                 "wav": "audio/wav",
    #                 "flac": "audio/flac",
    #                 "aac": "audio/aac",
    #                 "ogg": "audio/ogg",
    #                 "m4a": "audio/mp4",
    #             }.get(ext, "audio/mpeg")
    #             src = f"data:{mime};base64,{base64_data}"
    #         else:
    #             # If we couldn't get the file data, fallback to the file path
    #             src = file.path

    #         # Remove any previous audio control if present
    #         if audio_player:
    #             page.controls.remove(audio_player)
            
    #         # Create and add the Audio control that auto-plays the file
    #         audio_player = ft.Audio(src=src, autoplay=True, controls=True)
    #         page.add(audio_player)
    #         page.update()

    # Create the FilePicker and add it to the page overlay
    
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
