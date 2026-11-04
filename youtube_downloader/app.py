import argparse
import os
import queue
import re
import shutil
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

import yt_dlp

try:
    import imageio_ffmpeg
except ImportError:
    imageio_ffmpeg = None

from .update_check import main as check_updates

APP_NAME = "YouTube-Downloader"
ICON_RESOURCE = "assets/icone.png"


def sanitize_folder_name(name):
    cleaned = re.sub(r"[\\/:*?\"<>|]+", "_", name).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned or "Playlist"


def build_output_template(output_dir, is_playlist, playlist_name):
    if is_playlist:
        folder_name = sanitize_folder_name(playlist_name or "%(playlist_title)s")
        return os.path.join(output_dir, folder_name, "%(playlist_index)03d - %(title)s.%(ext)s")

    return os.path.join(output_dir, "%(title)s.%(ext)s")


def find_bundled_ffmpeg():
    if imageio_ffmpeg is None:
        return None
    try:
        return imageio_ffmpeg.get_ffmpeg_exe()
    except RuntimeError:
        return None


def build_ydl_options(output_dir, is_playlist, playlist_name, media_type, logger_callback):
    outtmpl = build_output_template(output_dir, is_playlist, playlist_name)
    common_options = {
        "outtmpl": outtmpl,
        "retries": 10,
        "fragment_retries": 10,
        "extractor_retries": 5,
        "socket_timeout": 30,
        "noplaylist": not is_playlist,
        "progress_hooks": [logger_callback],
        "ignoreerrors": False,
        "windowsfilenames": True,
    }

    ffmpeg_path = find_bundled_ffmpeg()
    if ffmpeg_path:
        common_options["ffmpeg_location"] = ffmpeg_path

    if media_type == "audio":
        common_options.update(
            {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            }
        )
    else:
        common_options.update(
            {
                "format": "bestvideo+bestaudio/best",
                "merge_output_format": "mp4",
            }
        )

    return common_options


def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def default_output_dir():
    home = os.path.expanduser("~")
    for name in ("Downloads", "Téléchargements"):
        candidate = os.path.join(home, name)
        if os.path.isdir(candidate):
            return candidate
    return home


def find_desktop_folder():
    home = os.path.expanduser("~")
    for name in ("Desktop", "Bureau"):
        candidate = os.path.join(home, name)
        if os.path.isdir(candidate):
            return candidate
    return None


def desktop_exec_value(path):
    # Spécification Desktop Entry : règle de citation de Exec, puis échappement
    # des chaînes (les antislashs sont donc doublés deux fois).
    quoted = re.sub(r'(["`$\\])', r"\\\1", path)
    return '"' + quoted.replace("\\", "\\\\").replace("%", "%%") + '"'


def write_if_changed(path, content):
    try:
        with open(path, "rb") as existing:
            if existing.read() == content:
                return
    except FileNotFoundError:
        pass
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as target:
        target.write(content)


def install_linux_launcher():
    if not (getattr(sys, "frozen", False) and sys.platform.startswith("linux")):
        return

    # L'application doit démarrer même si le lanceur ne peut pas être installé.
    try:
        data_home = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
        icon_path = os.path.join(data_home, "icons", "hicolor", "512x512", "apps", "youtube-downloader.png")
        with open(resource_path(ICON_RESOURCE), "rb") as icon_file:
            write_if_changed(icon_path, icon_file.read())

        entry = "\n".join(
            [
                "[Desktop Entry]",
                "Type=Application",
                "Name=YouTube Downloader",
                "Comment=Télécharger des vidéos ou de l'audio depuis YouTube",
                f"Exec={desktop_exec_value(sys.executable)}",
                "Icon=" + icon_path.replace("\\", "\\\\"),
                "Terminal=false",
                "Categories=Network;",
                # Tk normalise la classe de fenêtre : « Youtube-downloader ».
                f"StartupWMClass={APP_NAME.capitalize()}",
                "",
            ]
        )
        menu_path = os.path.join(data_home, "applications", "youtube-downloader.desktop")
        first_launch = not os.path.exists(menu_path)
        write_if_changed(menu_path, entry.encode("utf-8"))

        # Un exécutable Linux ne contient pas d'icône : seul un lanceur peut en afficher une.
        # Créé au premier lancement seulement, pour ne pas revenir si la personne le supprime.
        desktop_folder = find_desktop_folder()
        if desktop_folder:
            shortcut_path = os.path.join(desktop_folder, "youtube-downloader.desktop")
            if first_launch or os.path.exists(shortcut_path):
                write_if_changed(shortcut_path, entry.encode("utf-8"))
                os.chmod(shortcut_path, 0o755)
    except (OSError, ValueError):
        pass


def create_fallback_icon(root):
    icon = tk.PhotoImage(width=32, height=32)
    icon.put("#0f172a", to=(0, 0, 32, 32))
    icon.put("#1d4ed8", to=(3, 3, 29, 29))
    icon.put("#ffffff", to=(12, 9, 20, 23))
    icon.put("#60a5fa", to=(11, 10, 19, 22))
    icon.put("#f8fafc", to=(14, 12, 17, 20))
    root.iconphoto(True, icon)
    root._app_icon = icon


def create_app_icon(root):
    icon_path = resource_path(ICON_RESOURCE)
    try:
        icon = tk.PhotoImage(file=icon_path)
        root.iconphoto(True, icon)
        root._app_icon = icon
    except tk.TclError:
        create_fallback_icon(root)


class InfoWindow(tk.Toplevel):
    def __init__(self, parent, title, body_lines):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        frame = ttk.Frame(self, padding=18)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text=title, font=("TkDefaultFont", 14, "bold")).pack(anchor="w")

        text = tk.Text(frame, width=66, height=12, wrap=tk.WORD, borderwidth=0)
        text.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        text.insert(tk.END, "\n\n".join(body_lines))
        text.configure(state=tk.DISABLED)

        ttk.Button(frame, text="Fermer", command=self.destroy).pack(anchor="e", pady=(12, 0))

        self.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        x = parent_x + max(20, (parent_width - window_width) // 2)
        y = parent_y + max(20, (parent_height - window_height) // 2)
        self.geometry(f"+{x}+{y}")


def build_terms_text():
    return [
        "Cet outil est destiné à un usage légal, personnel et autorisé uniquement.",
        "Télécharger du contenu YouTube sans les droits, l'autorisation ou une base légale valable peut enfreindre les conditions de YouTube et le droit d'auteur applicable.",
        "Il vous appartient de vérifier que vous avez le droit de télécharger, de conserver et d'utiliser tout contenu traité par cette application.",
        "L'auteur n'approuve pas le téléchargement ni la redistribution non autorisés de contenus protégés.",
    ]


def build_about_text():
    return [
        "Auteur : J. Jifferson Delly",
        "Portfolio : https://dellyjifferson.engineer",
        "Un petit outil Tkinter pour enregistrer des vidéos ou de l'audio avec yt-dlp.",
    ]


class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("780x620")
        self.root.minsize(720, 560)

        create_app_icon(self.root)

        self.message_queue = queue.Queue()
        self.download_thread = None

        self.url_var = tk.StringVar(value="")
        self.output_dir_var = tk.StringVar(value=default_output_dir())
        self.playlist_var = tk.BooleanVar(value=False)
        self.playlist_name_var = tk.StringVar()
        self.media_type_var = tk.StringVar(value="video")
        self.status_var = tk.StringVar(value="Prêt")

        self._build_ui()
        self._set_playlist_state()
        self._poll_queue()

    def _build_ui(self):
        menu_bar = tk.Menu(self.root)
        help_menu = tk.Menu(menu_bar, tearoff=False)
        help_menu.add_command(label="À propos", command=self.show_about)
        help_menu.add_command(label="Conditions d'utilisation", command=self.show_terms)
        menu_bar.add_cascade(label="Aide", menu=help_menu)
        self.root.config(menu=menu_bar)

        container = ttk.Frame(self.root, padding=18)
        container.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(container, text="YouTube Downloader", font=("TkDefaultFont", 18, "bold"))
        title.pack(anchor="w", pady=(0, 10))

        subtitle = ttk.Label(
            container,
            text="Téléchargez une vidéo ou une playlist, en vidéo ou en audio, avec de nouvelles tentatives automatiques en cas de coupure réseau.",
            wraplength=720,
        )
        subtitle.pack(anchor="w", pady=(0, 16))

        form = ttk.Frame(container)
        form.pack(fill=tk.X)

        self._add_labeled_entry(form, "Adresse (URL) de la vidéo ou de la playlist", self.url_var, row=0)
        self._add_output_picker(form, row=1)
        self._add_playlist_controls(form, row=2)
        self._add_media_controls(form, row=3)

        actions = ttk.Frame(container)
        actions.pack(fill=tk.X, pady=(8, 10))

        self.download_button = ttk.Button(actions, text="Lancer le téléchargement", command=self.start_download)
        self.download_button.pack(side=tk.LEFT)

        ttk.Button(actions, text="Effacer le journal", command=self.clear_log).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(actions, text="Conditions", command=self.show_terms).pack(side=tk.RIGHT)
        ttk.Button(actions, text="À propos", command=self.show_about).pack(side=tk.RIGHT, padx=(0, 8))

        self.progress = ttk.Progressbar(container, mode="indeterminate")
        self.progress.pack(fill=tk.X, pady=(6, 6))

        status_row = ttk.Frame(container)
        status_row.pack(fill=tk.X)

        ttk.Label(status_row, textvariable=self.status_var).pack(anchor="w")

        log_label = ttk.Label(container, text="Journal d'activité")
        log_label.pack(anchor="w", pady=(14, 4))

        self.log_widget = scrolledtext.ScrolledText(container, height=16, wrap=tk.WORD, state=tk.DISABLED)
        self.log_widget.pack(fill=tk.BOTH, expand=True)

    def _add_labeled_entry(self, parent, label_text, variable, row):
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, sticky="ew", pady=6)
        parent.columnconfigure(0, weight=1)
        ttk.Label(frame, text=label_text).pack(anchor="w")
        entry = ttk.Entry(frame, textvariable=variable)
        entry.pack(fill=tk.X, pady=(4, 0))

    def _add_output_picker(self, parent, row):
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, sticky="ew", pady=6)
        ttk.Label(frame, text="Dossier de destination").pack(anchor="w")

        picker = ttk.Frame(frame)
        picker.pack(fill=tk.X, pady=(4, 0))
        ttk.Entry(picker, textvariable=self.output_dir_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(picker, text="Parcourir", command=self.choose_output_folder).pack(side=tk.LEFT, padx=(8, 0))

    def _add_playlist_controls(self, parent, row):
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, sticky="ew", pady=6)

        ttk.Checkbutton(
            frame,
            text="Cette adresse est une playlist",
            variable=self.playlist_var,
            command=self._set_playlist_state,
        ).pack(anchor="w")

        playlist_row = ttk.Frame(frame)
        playlist_row.pack(fill=tk.X, pady=(6, 0))
        ttk.Label(playlist_row, text="Nom de la playlist").pack(anchor="w")
        self.playlist_entry = ttk.Entry(playlist_row, textvariable=self.playlist_name_var)
        self.playlist_entry.pack(fill=tk.X, pady=(4, 0))
        ttk.Label(
            playlist_row,
            text="Laissez vide pour utiliser le titre de la playlist sur YouTube.",
            foreground="#555555",
        ).pack(anchor="w", pady=(4, 0))

    def _add_media_controls(self, parent, row):
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, sticky="ew", pady=6)

        ttk.Label(frame, text="Type de téléchargement").pack(anchor="w")
        options = ttk.Frame(frame)
        options.pack(anchor="w", pady=(4, 0))
        ttk.Radiobutton(options, text="Vidéo", value="video", variable=self.media_type_var).pack(side=tk.LEFT)
        ttk.Radiobutton(options, text="Audio", value="audio", variable=self.media_type_var).pack(side=tk.LEFT, padx=(14, 0))

    def _set_playlist_state(self):
        state = tk.NORMAL if self.playlist_var.get() else tk.DISABLED
        self.playlist_entry.configure(state=state)

    def choose_output_folder(self):
        folder = filedialog.askdirectory(initialdir=self.output_dir_var.get() or default_output_dir())
        if folder:
            self.output_dir_var.set(folder)

    def clear_log(self):
        self.log_widget.configure(state=tk.NORMAL)
        self.log_widget.delete("1.0", tk.END)
        self.log_widget.configure(state=tk.DISABLED)

    def show_terms(self):
        InfoWindow(self.root, "Conditions d'utilisation", build_terms_text())

    def show_about(self):
        InfoWindow(self.root, "À propos", build_about_text())

    def log(self, message):
        self.message_queue.put(("log", message))

    def _append_log(self, message):
        self.log_widget.configure(state=tk.NORMAL)
        self.log_widget.insert(tk.END, message + "\n")
        self.log_widget.see(tk.END)
        self.log_widget.configure(state=tk.DISABLED)

    def _progress_hook(self, data):
        status = data.get("status")
        if status == "downloading":
            downloaded = data.get("downloaded_bytes") or 0
            total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
            percent = (downloaded / total * 100) if total else 0
            speed = data.get("speed")
            eta = data.get("eta")
            speed_text = f"{speed / 1024 / 1024:.2f} Mo/s" if speed else "vitesse inconnue"
            eta_text = f"{eta}s" if eta is not None else "durée inconnue"
            self.message_queue.put(
                (
                    "status",
                    f"Téléchargement : {percent:.1f} % - {speed_text} - temps restant : {eta_text}",
                )
            )
        elif status == "finished":
            filename = data.get("filename", "download")
            self.message_queue.put(("log", f"Téléchargement terminé : {filename}"))

    def start_download(self):
        if self.download_thread and self.download_thread.is_alive():
            messagebox.showinfo("Téléchargement en cours", "Un téléchargement est déjà en cours.")
            return

        url = self.url_var.get().strip()
        output_dir = self.output_dir_var.get().strip()
        playlist_name = self.playlist_name_var.get().strip()
        is_playlist = self.playlist_var.get()
        media_type = self.media_type_var.get()

        if not url:
            messagebox.showerror("Adresse manquante", "Veuillez saisir l'adresse d'une vidéo ou d'une playlist YouTube.")
            return

        if not output_dir:
            messagebox.showerror("Dossier manquant", "Veuillez choisir où enregistrer les fichiers.")
            return

        os.makedirs(output_dir, exist_ok=True)

        self.download_button.configure(state=tk.DISABLED)
        self.progress.start(10)
        self.status_var.set("Démarrage du téléchargement...")
        self.log(f"Démarrage du téléchargement ({'audio' if media_type == 'audio' else 'vidéo'}, {'playlist' if is_playlist else 'élément unique'})")

        self.download_thread = threading.Thread(
            target=self._download_worker,
            args=(url, output_dir, is_playlist, playlist_name, media_type),
            daemon=True,
        )
        self.download_thread.start()

    def _download_worker(self, url, output_dir, is_playlist, playlist_name, media_type):
        try:
            self.message_queue.put(("status", "Analyse de la vidéo et démarrage... Cela peut prendre un moment."))
            options = build_ydl_options(output_dir, is_playlist, playlist_name, media_type, self._progress_hook)
            with yt_dlp.YoutubeDL(options) as downloader:
                downloader.download([url])
            self.message_queue.put(("done", f"Téléchargement réussi, fichiers enregistrés dans {output_dir}"))
        except Exception as exc:
            self.message_queue.put(("error", str(exc)))

    def _poll_queue(self):
        try:
            while True:
                kind, payload = self.message_queue.get_nowait()
                if kind == "log":
                    self._append_log(payload)
                elif kind == "status":
                    self.status_var.set(payload)
                elif kind == "done":
                    self.progress.stop()
                    self.download_button.configure(state=tk.NORMAL)
                    self.status_var.set("Terminé")
                    self._append_log(payload)
                    messagebox.showinfo("Réussite", payload)
                elif kind == "error":
                    self.progress.stop()
                    self.download_button.configure(state=tk.NORMAL)
                    self.status_var.set("Échec")
                    self._append_log(f"Erreur : {payload}")
                    messagebox.showerror("Échec du téléchargement", payload)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self._poll_queue)


def main(argv=None):
    parser = argparse.ArgumentParser(description="YouTube Downloader")
    parser.add_argument("--check-updates", action="store_true", help="Check for app updates and exit")
    args = parser.parse_args(argv)

    if args.check_updates:
        check_updates()
        return

    install_linux_launcher()
    root = tk.Tk(className=APP_NAME)
    app = YouTubeDownloaderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
