from __future__ import annotations

import json
import urllib.error
import urllib.request
from importlib import metadata

PACKAGE_NAME = "youtube-downloader"
PROJECT_URL = "https://pypi.org/pypi/youtube-downloader/json"


def _version_tuple(value: str) -> tuple[int, ...]:
    parts = []
    for piece in value.split("."):
        if piece.isdigit():
            parts.append(int(piece))
        else:
            break
    return tuple(parts)


def _fetch_latest_version() -> str | None:
    request = urllib.request.Request(PROJECT_URL, headers={"User-Agent": "youtube-downloader-update-check/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.load(response)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None

    return payload.get("info", {}).get("version")


def main() -> None:
    installed_version = metadata.version(PACKAGE_NAME)
    latest_version = _fetch_latest_version()

    if not latest_version:
        print(f"Installed version: {installed_version}")
        print("Update check: unavailable")
        return

    print(f"Installed version: {installed_version}")
    print(f"Latest version: {latest_version}")

    if _version_tuple(latest_version) > _version_tuple(installed_version):
        print("Update available")
    else:
        print("You are up to date")


if __name__ == "__main__":
    main()
