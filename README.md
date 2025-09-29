### TermTorrent

Minimal command line utility for downloading torrents in your terminal.

Minimal utilities to:
- Create a `.torrent` file from a folder (trackerless, DHT-enabled) using `torf`.
- Get Torrent metadata.
- Download a `.torrent` using `libtorrent`.
---

### Prerequisites
- Python 3.10+ (project was tested with Python 3.13)
- macOS, Linux, or Windows

Note about `libtorrent` wheels:
- On macOS and Windows, `pip` will typically install a prebuilt `libtorrent` wheel. If you encounter installation issues, try: `pip install --upgrade pip` and then reinstall requirements. As a fallback, search for prebuilt wheels compatible with your platform and Python version.

---

### Setup (create and activate a virtual environment)

macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Windows (PowerShell):
```bash
py -m venv venv
venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

To deactivate later: `deactivate`

---

### How to run

#### 1) Create a .torrent from a folder
This creates a trackerless torrent that allows DHT (useful for private sharing without a tracker).

```bash
python -c "from create_torrent import create_torrent_from_folder; print(create_torrent_from_folder('/absolute/path/to/your/folder'))"
```

Output will be a `.torrent` file written to the current directory with the folder name, e.g. `YourFolder.torrent`.

Examples:
- macOS/Linux:
```bash
python -c "from create_torrent import create_torrent_from_folder; print(create_torrent_from_folder('/Users/you/TermTorrent/downloads'))"
```

#### 2) Download a .torrent
Downloads the content of a `.torrent` into `./downloads/` by default. Progress is handled internally; you can optionally pass a callback if integrating into your own app.

```bash
python -c "from download_torrent import download_torrent; download_torrent('/absolute/path/to/file.torrent', './downloads/')"
```

Examples:
```bash
python -c "from download_torrent import download_torrent; download_torrent('/Users/you/TermTorrent/Hacking For Dummies, 8th Edition.torrent', './downloads/')"
```

Optional: simple progress printing via one-liner callback
```bash
python -c "import threading; from download_torrent import download_torrent; print_progress=lambda p: print(f'Progress: {p}%'); download_torrent('/absolute/path/to/file.torrent', './downloads/', progress_callback=print_progress, cancel_event=threading.Event())"
```

---

### Project files of interest
- `create_torrent.py` – builds a `.torrent` from a given folder.
- `download_torrent.py` – downloads a `.torrent` using `libtorrent`.
- `requirements.txt` – pinned dependencies.

The provided `main.py` is a placeholder used to verify environment setup (it prints the installed `textual` version). It is not required for torrent operations.

---

### Troubleshooting
- If `pip install -r requirements.txt` fails on `libtorrent`, upgrade `pip` and retry. Ensure your Python version matches an available wheel.
- On Apple Silicon (M1/M2/M3), prefer a recent Python version (3.11+) and ensure your terminal runs under the same architecture as your Python environment (avoid mixing arm64 and x86_64).
- On Linux, you may need system libraries for `libtorrent` if a wheel isn’t available. Consult your distro’s documentation or use a compatible wheel.

---


