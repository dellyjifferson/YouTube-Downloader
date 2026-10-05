#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

source "$ROOT_DIR/.env/bin/activate"

python -m PyInstaller \
  --clean \
  --noconfirm \
  --onefile \
  --windowed \
  --name "YouTube-Downloader" \
  --add-data "youtube_downloader/youtube_downloader.png:youtube_downloader" \
  "youtube_downloader/app.py"
