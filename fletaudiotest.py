import flet as ft

def main(page: ft.Page):
    audio1 = ft.Audio(
        src="/Users/macbook/Documents/PROGRAMS/Flet/Music-Organizer/Songs/19-2000.wav", autoplay=True
    )
    page.overlay.append(audio1)
    page.add(
        ft.Text("This is an app with background audio."),
        ft.ElevatedButton("Stop playing", on_click=lambda _: audio1.pause()),
    )

ft.app(main)