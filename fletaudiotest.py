import flet as ft

def main(page: ft.Page):
    audio1 = ft.Audio(
        src="/Users/macbook/Documents/PROGRAMS/STEAM/assets/press.wav", autoplay=True
    )
    page.overlay.append(audio1)
    page.add(
        ft.Text("This is an app with background audio."),
        ft.ElevatedButton("Stop playing", on_click=lambda _: audio1.play()),
    )

ft.app(main)