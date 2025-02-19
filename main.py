import flet as ft
import base64
import os

def main(page: ft.Page):
    audio_player = None  # To store the audio control

    def on_file_selected(e: ft.FilePickerResultEvent):
        nonlocal audio_player
        if e.files:
            # Allowed music file extensions
            allowed_extensions = {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"}
            file = e.files[0]
            
            # Validate the file extension
            if not any(file.name.lower().endswith(ext) for ext in allowed_extensions):
                page.add(ft.Text("Invalid file type! Please select a music file."))
                page.update()
                return

            # Try to get file bytes if available, otherwise read from file.path
            file_data = None
            if hasattr(file, "bytes"):
                file_data = file.bytes

            if file_data is None and file.path:
                try:
                    with open(file.path, "rb") as f:
                        file_data = f.read()
                except Exception as ex:
                    page.add(ft.Text(f"Error reading file: {ex}"))
                    page.update()
                    return

            if file_data is not None:
                # Convert the file data to a base64 string and create a data URL
                base64_data = base64.b64encode(file_data).decode("utf-8")
                ext = file.name.lower().rsplit(".", 1)[-1]
                mime = {
                    "mp3": "audio/mpeg",
                    "wav": "audio/wav",
                    "flac": "audio/flac",
                    "aac": "audio/aac",
                    "ogg": "audio/ogg",
                    "m4a": "audio/mp4",
                }.get(ext, "audio/mpeg")
                src = f"data:{mime};base64,{base64_data}"
            else:
                # If we couldn't get the file data, fallback to the file path
                src = file.path

            # Remove any previous audio control if present
            if audio_player:
                page.controls.remove(audio_player)
            
            # Create and add the Audio control that auto-plays the file
            audio_player = ft.Audio(src=src, autoplay=True, controls=True)
            page.add(audio_player)
            page.update()

    # Create the FilePicker and add it to the page overlay
    file_picker = ft.FilePicker(on_result=on_file_selected)
    page.overlay.append(file_picker)

    # Add a button to trigger file picking
    page.add(
        ft.ElevatedButton(
            "Pick a music file",
            on_click=lambda e: file_picker.pick_files(allow_multiple=False),
        )
    )

ft.app(target=main)
