from torf import Torrent
import os

def create_torrent_from_folder(folder_path: str) -> str:
    """
    Creates a torrent file for the folder at folder_path.
    Saves the torrent file in the current directory with the same name as the folder.
    Returns a status message.
    """
    try:
        # Normalize folder name for output filename
        folder_name = os.path.basename(os.path.normpath(folder_path))
        # Create torrent without trackers (trackerless)
        t = Torrent(
            path=folder_path,
            trackers=[],
            comment='Generated torrent without tracker'
        )
        t.private = False  # Allow DHT
        t.generate()

        # Save with same name + .torrent extension
        output_file = folder_name + ".torrent"
        t.write(output_file)

        return f"Torrent created successfully: {output_file}"
    except Exception as e:
        return f"Failed to create torrent: {e}"
