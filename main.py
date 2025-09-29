import os
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Event

from dump import dump_torrent_info
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, ListView, ListItem, Label, Button, ProgressBar
from textual.containers import Container
from textual.binding import Binding
from textual.reactive import reactive
from textual import on


class TermTorrent(App):
    CSS = """
    #heading {
        text-align: center;
        background: #0077b6;
        color: white;
        content-align: center middle;
        height: 3;
        text-style: bold;
        border: round gold;
        margin-bottom: 1;
    }
    #menu {
        border: round blue;
        padding: 1 2;
        background: black;
        color: cyan;
        text-style: bold;
    }
    #message {
        border: round green;
        padding: 1;
        margin-top: 1;
        color: yellow;
        text-style: italic;
    }
    #file_selector {
        border: round purple;
        height: 10;
        width: 60;
        margin-top: 1;
    }
    #progress_bar {
        margin-top: 1;
    }
    #cancel_button {
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("1", "create_torrent", "Create Torrent"),
        Binding("2", "dump", "Dump"),
        Binding("3", "download", "Download"),
        Binding("4", "exit_app", "Exit"),
    ]

    message_text = reactive("")
    file_selection_mode = reactive(False)
    selected_file = reactive("")
    downloading = reactive(False)

    def on_mount(self) -> None:
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.cancel_event = Event()
        self.query_one("#progress_bar").display = False
        self.query_one("#cancel_button").display = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Static("TermTorrent", id="heading")
        menu_text = (
            "1. Create Torrent from a folder\n"
            "2. Dump (select .torrent file)\n"
            "3. Download\n"
            "4. Exit\n"
            "\nPress the corresponding number (1-4) to choose an option."
        )
        yield Container(Static(menu_text, id="menu"))
        yield Static("", id="message")
        yield ProgressBar(id="progress_bar")
        yield Button("Cancel Download", id="cancel_button")
        yield Footer()

    def watch_message_text(self, new_value: str) -> None:
        widget = self.query_one("#message", Static)
        if widget:
            widget.update(new_value)

    def start_download_ui(self):
        self.downloading = True
        self.cancel_event.clear()
        self.query_one("#progress_bar").display = True
        self.query_one("#progress_bar").value = 0
        self.query_one("#cancel_button").display = True

    def stop_download_ui(self):
        self.downloading = False
        self.query_one("#progress_bar").display = False
        self.query_one("#cancel_button").display = False

    def update_progress(self, progress: int):
        self.call_later(lambda: setattr(self.query_one("#progress_bar"), "value", progress))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if self.downloading and event.button.id == "cancel_button":
            self.cancel_event.set()
            self.message_text = "Download cancellation requested..."

    def action_create_torrent(self) -> None:
        self.message_text = "Select a folder to create torrent:"
        self.file_selection_mode = "folder"
        menu = self.query_one("#menu")
        menu.remove()

        folders = [f for f in os.listdir(".") if os.path.isdir(f)]
        if not folders:
            self.message_text = "No folders found."
            self.file_selection_mode = False
            self.mount(Static("No folders found. Returning to menu.", id="menu"))
            return

        self.folder_selector = ListView(id="file_selector")
        self.mount(self.folder_selector)
        for folder in folders:
            item = ListItem(Label(folder))
            item.foldername = folder
            self.folder_selector.append(item)
        self.folder_selector.focus()

    def action_dump(self) -> None:
        self.message_text = "Select a .torrent file:"
        self.file_selection_mode = "dump"
        menu = self.query_one("#menu")
        menu.remove()

        torrents = [f for f in os.listdir(".") if f.endswith(".torrent")]
        if not torrents:
            self.message_text = "No .torrent files found."
            self.file_selection_mode = False
            self.mount(Static("No .torrent files found. Returning to menu.", id="menu"))
            return

        self.file_selector = ListView(id="file_selector")
        self.mount(self.file_selector)
        for torrent_file in torrents:
            item = ListItem(Label(torrent_file))
            item.filename = torrent_file
            self.file_selector.append(item)
        self.file_selector.focus()

    def action_download(self) -> None:
        self.message_text = "Select a .torrent file to download:"
        self.file_selection_mode = "download"
        menu = self.query_one("#menu")
        menu.remove()

        torrents = [f for f in os.listdir(".") if f.endswith(".torrent")]
        if not torrents:
            self.message_text = "No .torrent files found."
            self.file_selection_mode = False
            self.mount(Static("No .torrent files found. Returning to menu.", id="menu"))
            return

        self.file_selector = ListView(id="file_selector")
        self.mount(self.file_selector)
        for torrent_file in torrents:
            item = ListItem(Label(torrent_file))
            item.filename = torrent_file
            self.file_selector.append(item)
        self.file_selector.focus()

    @on(ListView.Selected)
    async def handle_item_selected(self, event: ListView.Selected) -> None:
        list_item = event.item

        if self.file_selection_mode == "folder":
            foldername = getattr(list_item, "foldername", None)
            if not foldername:
                self.message_text = "Error: Folder name is empty."
                return
            from create_torrent import create_torrent_from_folder
            result_msg = create_torrent_from_folder(foldername)
            self.message_text = result_msg

        elif self.file_selection_mode == "dump":
            filename = getattr(list_item, "filename", None)
            if not filename:
                self.message_text = "Error: Filename is empty."
                return
            dump_output = dump_torrent_info(filename)
            self.message_text = dump_output

        elif self.file_selection_mode == "download":
            filename = getattr(list_item, "filename", None)
            if not filename:
                self.message_text = "Error: Filename is empty."
                return

            from download_torrent import download_torrent
            from functools import partial

            self.message_text = f"Downloading: {filename} ..."
            self.start_download_ui()
            future = self.executor.submit(
                partial(download_torrent, filename, save_path="./downloads/",
                        progress_callback=self.update_progress, cancel_event=self.cancel_event)
            )

            def done_callback(fut):
                self.call_later(self.stop_download_ui)
                try:
                    fut.result()
                    if self.cancel_event.is_set():
                        self.message_text = f"Download cancelled: {filename}"
                    else:
                        self.message_text = f"Download complete: {filename}"
                except Exception as e:
                    self.message_text = f"Download error: {e}"

            future.add_done_callback(done_callback)

        else:
            self.message_text = "Error: No valid file or folder selected."

        event.list_view.remove()
        menu_text = (
            "1. Create Torrent from a folder\n"
            "2. Dump (select .torrent file)\n"
            "3. Download\n"
            "4. Exit\n"
            "\nPress the corresponding number (1-4) to choose an option."
        )
        self.mount(Static(menu_text, id="menu"))
        self.file_selection_mode = False

    def action_exit_app(self) -> None:
        self.exit()


if __name__ == "__main__":
    TermTorrent().run()
