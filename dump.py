import torrent_parser as tp

def dump_torrent_info(file_path: str) -> str:
    try:
        metadata = tp.parse_torrent_file(file_path)
        announce = metadata.get('announce', 'N/A')
        creation_date = metadata.get('creation date', 'N/A')
        comment = metadata.get('comment', 'N/A')
        info = metadata.get('info', {})
        name = info.get('name', 'N/A')
        files = info.get('files', [])
        piece_length = info.get('piece length', 0)
        piece_length_mb = piece_length / (1024 * 1024) if piece_length else 0
        output = [
            f"Torrent Name: {name}",
            f"Announce URL: {announce}",
            f"Creation Date: {creation_date}",
            f"Comment: {comment}",
            f"Size of Each Piece: {piece_length} bytes ({piece_length_mb:.2f} MB)",
            "Files:"
        ]
        if files:
            for f in files[:3]:
                file_path = "/".join(f.get('path', []))
                size_bytes = f.get('length', 0)
                size_mb = size_bytes / (1024 * 1024)
                output.append(f"  - {file_path} ({size_bytes} bytes, {size_mb:.2f} MB)")
        else:
            length = info.get('length', 0)
            length_mb = length / (1024 * 1024)
            output.append(f"  - {name} ({length} bytes, {length_mb:.2f} MB)")
        return "\n".join(output)
    except Exception as e:
        return f"Failed to parse torrent: {e}"
