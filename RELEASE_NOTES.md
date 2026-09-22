# Packaging and release notes

## Install on Linux

Use a clean Linux environment, then build and run the app locally:

```bash
python -m venv .env
source .env/bin/activate
pip install yt-dlp pyinstaller
chmod +x build_linux_executable.sh
./build_linux_executable.sh
./dist/YouTube-Downloader
```

PyInstaller places the executable in `dist/YouTube-Downloader`.

## Icon

The app now uses the `youtube_downloader.png` icon asset for the window and packaged executable.

## Windows installer build

Build Windows artifacts from a clean Windows VM or machine, not from a modified or packed executable.

```powershell
py -3 -m venv .env
.\.env\Scripts\activate
pip install yt-dlp pyinstaller
pyinstaller --clean --noconfirm --onefile --windowed --name "YouTube-Downloader" --add-data "youtube_downloader.png;." "YouTube downloader.py"
```

To create an installer, wrap the signed executable with a Windows installer tool such as Inno Setup or WiX. Keep the installer simple and avoid packers or obfuscators.

## Windows build and antivirus flagging

Yes, you can build a Windows version with PyInstaller, but no one can guarantee it will never be flagged by antivirus software. The usual way to reduce false positives is:

1. Use a clean build environment.
2. Sign the executable with a trusted code-signing certificate.
3. Avoid packers/obfuscators and ship a reproducible build.
4. Publish the source and release hashes.

Without a reputable code-signing certificate, Windows SmartScreen and some antivirus engines may still warn users, even when the app is legitimate.

## How to use a trusted certificate

Use a trusted code-signing certificate only on Windows artifacts, after you build them in a clean environment.

1. Obtain a code-signing certificate from a trusted CA.
2. Keep the private key in a secure location, such as a hardware token or a protected `.pfx` file.
3. Sign the executable and installer with Microsoft's `signtool`.
4. Add a trusted timestamp so the signature stays valid after the certificate expires.

Example signing commands:

```powershell
signtool sign /fd SHA256 /f "path\to\certificate.pfx" /p "YOUR_PFX_PASSWORD" /tr http://timestamp.digicert.com /td SHA256 "dist\YouTube-Downloader.exe"
signtool sign /fd SHA256 /f "path\to\certificate.pfx" /p "YOUR_PFX_PASSWORD" /tr http://timestamp.digicert.com /td SHA256 "installer\YouTube-Downloader-Setup.exe"
```

If you use a hardware token or cloud signing service, follow the certificate provider's signing instructions instead of embedding the private key in a file.

## Release checklist

1. Build from a clean environment.
2. Sign the Windows executable and installer with a trusted certificate.
3. Rebuild without packers or obfuscators so the output stays reproducible.
4. Publish the source archive, installer hashes, and executable hashes with the release.
