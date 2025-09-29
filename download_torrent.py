import libtorrent as lt
import time
import os

def download_torrent(torrent_path: str, save_path: str = "./downloads/", progress_callback=None, cancel_event=None) -> None:
    """
    Download a torrent file with progress updates and cancellation.

    Args:
        torrent_path (str): Path to the .torrent file.
        save_path (str): Directory to save downloaded files.
        progress_callback (func): Optional function(progress_percent:int) to report progress.
        cancel_event (threading.Event): Optional event to cancel the download.
    """
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # Load torrent info
    info = lt.torrent_info(torrent_path)

    # Create session and add torrent params
    ses = lt.session()
    params = {'ti': info, 'save_path': save_path}

    handle = ses.add_torrent(params)

    while not handle.is_seed():
        # Check for cancellation
        if cancel_event and cancel_event.is_set():
            ses.remove_torrent(handle)
            return  # Cancel immediately

        status = handle.status()
        progress = int(status.progress * 100)

        # Call the progress callback if provided
        if progress_callback:
            progress_callback(progress)

        time.sleep(1)
