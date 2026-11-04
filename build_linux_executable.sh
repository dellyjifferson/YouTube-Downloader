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
  --icon "youtube_downloader/assets/icone.png" \
  --add-data "youtube_downloader/assets/icone.png:assets" \
  "YouTube downloader.py"
