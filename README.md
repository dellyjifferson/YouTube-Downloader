# YouTube Downloader

A simple and user-friendly GUI application to download videos or audio from YouTube, including playlist support.

## Features

- **Video & Audio Downloads**: Download videos in best quality (mp4) or extract audio (mp3)
- **Playlist Support**: Download entire playlists with automatic folder organization
- **Custom Output Folder**: Choose where to save downloaded content
- **Robust Downloading**: Built-in retries and longer network timeouts for reliable downloads
- **Activity Log**: Real-time logging of download progress and status
- **Cross-Platform**: Works on Linux and Windows

## Requirements

- Python 3.7 or higher
- FFmpeg (for audio extraction)
- pip (Python package manager)

### System Dependencies

**On Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip ffmpeg
```

**On macOS:**
```bash
brew install python ffmpeg
```

**On Windows:**
- Install Python from [python.org](https://www.python.org/downloads/)
- Install FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html) or use: `choco install ffmpeg`

## Installation

### Option 1: Run from Source (Recommended for Development)

1. Clone or download this repository
2. Navigate to the project directory:
   ```bash
   cd youtube_downloader
   ```

3. Create a virtual environment:
   ```bash
   python -m venv .env
   ```

4. Activate the virtual environment:
   - On Linux/macOS:
     ```bash
     source .env/bin/activate
     ```
   - On Windows:
     ```bash
     .\.env\Scripts\activate
     ```

5. Install dependencies:
   ```bash
   pip install yt-dlp
   ```

6. Run the application:
   ```bash
   python "YouTube downloader.py"
   ```

### Option 2: Build Standalone Executable

#### Linux
```bash
python -m venv .env
source .env/bin/activate
pip install yt-dlp pyinstaller
chmod +x build_linux_executable.sh
./build_linux_executable.sh
./dist/YouTube-Downloader
```

#### Windows
```powershell
py -3 -m venv .env
.\.env\Scripts\activate
pip install yt-dlp pyinstaller
pyinstaller --clean --noconfirm --onefile --windowed --name "YouTube-Downloader" --add-data "youtube_downloader.png;." "YouTube downloader.py"
.\dist\YouTube-Downloader.exe
```

## Usage

1. **Enter a URL**: Paste a YouTube video or playlist URL
2. **Select Output Folder**: Click "Browse" to choose where files will be saved
3. **Choose Download Type**:
   - Select "Video" to download video files (mp4)
   - Select "Audio" to download and convert to audio (mp3)
4. **Playlist Option** (Optional):
   - Check "Treat URL as playlist" if downloading multiple videos
   - Optionally specify a custom playlist folder name
5. **Start Download**: Click "Start Download" button
6. **Monitor Progress**: Watch the activity log for real-time status

## Legal Notice

**Important**: This tool is provided for lawful, personal, and authorized use only. Downloading YouTube content without proper rights, permission, or a valid legal basis may violate YouTube's Terms of Service and applicable copyright laws.

You are responsible for:
- Ensuring you have the right to download and use the content
- Complying with local laws and regulations
- Respecting copyright and intellectual property rights

The author does not endorse unauthorized downloading or redistribution of protected content.

## Project Information

- **Author**: J. Jifferson Delly
- **Portfolio**: https://dellyjifferson.engineer
- **Built with**: Python, Tkinter, yt-dlp

## Troubleshooting

**Issue: "FFmpeg not found"**
- Make sure FFmpeg is installed and added to your system PATH

**Issue: "Certificate verify failed"**
- This is usually a network/SSL issue. Try updating certificates or checking your internet connection

**Issue: Download fails after starting**
- Check the activity log for specific error messages
- Ensure the output folder has write permissions
- Try downloading a single video first before attempting playlists

**Issue: Windows Defender warns about the executable**
- This is common for unsigned executables. It's safe if built from source. To reduce warnings, obtain a code-signing certificate.

## License

This project is provided as-is for personal use.
