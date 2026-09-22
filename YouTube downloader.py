import os
import queue
import re
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

import yt_dlp


def sanitize_folder_name(name):
    cleaned = re.sub(r"[\\/:*?\"<>|]+", "_", name).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned or "Playlist"


def build_output_template(output_dir, is_playlist, playlist_name):
    if is_playlist:
        folder_name = sanitize_folder_name(playlist_name or "%(playlist_title)s")
        return os.path.join(output_dir, folder_name, "%(playlist_index)03d - %(title)s.%(ext)s")

    return os.path.join(output_dir, "%(title)s.%(ext)s")


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
    icon_path = resource_path("youtube_downloader.png")
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

        ttk.Button(frame, text="Close", command=self.destroy).pack(anchor="e", pady=(12, 0))

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
        "Terms and conditions",
        "This tool is provided for lawful, personal, and authorized use only.",
        "Downloading YouTube content without the rights, permission, or a valid legal basis may violate YouTube's terms and applicable copyright law.",
        "You are responsible for confirming that you have the right to download, store, and use any content processed by this application.",
        "The author does not endorse unauthorized downloading or redistribution of protected content.",
    ]


def build_about_text():
    return [
        "About",
        "Author: J. Jifferson Delly",
        "Portfolio: https://dellyjifferson.engineer",
        "A small Tkinter-based downloader for saving videos or audio with yt-dlp.",
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
        self.output_dir_var = tk.StringVar(value=os.getcwd())
        self.playlist_var = tk.BooleanVar(value=False)
        self.playlist_name_var = tk.StringVar()
        self.media_type_var = tk.StringVar(value="video")
        self.status_var = tk.StringVar(value="Ready")

        self._build_ui()
        self._set_playlist_state()
        self._poll_queue()

    def _build_ui(self):
        menu_bar = tk.Menu(self.root)
        help_menu = tk.Menu(menu_bar, tearoff=False)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Terms and Conditions", command=self.show_terms)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menu_bar)

        container = ttk.Frame(self.root, padding=18)
        container.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(container, text="YouTube Downloader", font=("TkDefaultFont", 18, "bold"))
        title.pack(anchor="w", pady=(0, 10))

        subtitle = ttk.Label(
            container,
            text="Download a single video or a playlist as video or audio, with retries and a longer network timeout.",
            wraplength=720,
        )
        subtitle.pack(anchor="w", pady=(0, 16))

        form = ttk.Frame(container)
        form.pack(fill=tk.X)

        self._add_labeled_entry(form, "Video or playlist URL", self.url_var, row=0)
        self._add_output_picker(form, row=1)
        self._add_playlist_controls(form, row=2)
        self._add_media_controls(form, row=3)

        actions = ttk.Frame(container)
        actions.pack(fill=tk.X, pady=(8, 10))

        self.download_button = ttk.Button(actions, text="Start Download", command=self.start_download)
        self.download_button.pack(side=tk.LEFT)

        ttk.Button(actions, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(actions, text="Terms", command=self.show_terms).pack(side=tk.RIGHT)
        ttk.Button(actions, text="About", command=self.show_about).pack(side=tk.RIGHT, padx=(0, 8))

        self.progress = ttk.Progressbar(container, mode="indeterminate")
        self.progress.pack(fill=tk.X, pady=(6, 6))

        status_row = ttk.Frame(container)
        status_row.pack(fill=tk.X)

        ttk.Label(status_row, textvariable=self.status_var).pack(anchor="w")

        log_label = ttk.Label(container, text="Activity log")
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
        ttk.Label(frame, text="Output folder").pack(anchor="w")

        picker = ttk.Frame(frame)
        picker.pack(fill=tk.X, pady=(4, 0))
        ttk.Entry(picker, textvariable=self.output_dir_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(picker, text="Browse", command=self.choose_output_folder).pack(side=tk.LEFT, padx=(8, 0))

    def _add_playlist_controls(self, parent, row):
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, sticky="ew", pady=6)

        ttk.Checkbutton(
            frame,
            text="Treat URL as playlist",
            variable=self.playlist_var,
            command=self._set_playlist_state,
        ).pack(anchor="w")

        playlist_row = ttk.Frame(frame)
        playlist_row.pack(fill=tk.X, pady=(6, 0))
        ttk.Label(playlist_row, text="Playlist name").pack(anchor="w")
        self.playlist_entry = ttk.Entry(playlist_row, textvariable=self.playlist_name_var)
        self.playlist_entry.pack(fill=tk.X, pady=(4, 0))
        ttk.Label(
            playlist_row,
            text="Leave this blank to use the playlist title from YouTube.",
            foreground="#555555",
        ).pack(anchor="w", pady=(4, 0))

    def _add_media_controls(self, parent, row):
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, sticky="ew", pady=6)

        ttk.Label(frame, text="Download type").pack(anchor="w")
        options = ttk.Frame(frame)
        options.pack(anchor="w", pady=(4, 0))
        ttk.Radiobutton(options, text="Video", value="video", variable=self.media_type_var).pack(side=tk.LEFT)
        ttk.Radiobutton(options, text="Audio", value="audio", variable=self.media_type_var).pack(side=tk.LEFT, padx=(14, 0))

    def _set_playlist_state(self):
        state = tk.NORMAL if self.playlist_var.get() else tk.DISABLED
        self.playlist_entry.configure(state=state)

    def choose_output_folder(self):
        folder = filedialog.askdirectory(initialdir=self.output_dir_var.get() or os.getcwd())
        if folder:
            self.output_dir_var.set(folder)

    def clear_log(self):
        self.log_widget.configure(state=tk.NORMAL)
        self.log_widget.delete("1.0", tk.END)
        self.log_widget.configure(state=tk.DISABLED)

    def show_terms(self):
        InfoWindow(self.root, "Terms and Conditions", build_terms_text())

    def show_about(self):
        InfoWindow(self.root, "About", build_about_text())

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
            speed_text = f"{speed / 1024 / 1024:.2f} MB/s" if speed else "unknown speed"
            eta_text = f"{eta}s" if eta is not None else "unknown ETA"
            self.message_queue.put(
                (
                    "status",
                    f"Downloading: {percent:.1f}% - {speed_text} - ETA {eta_text}",
                )
            )
        elif status == "finished":
            filename = data.get("filename", "download")
            self.message_queue.put(("log", f"Finished downloading {filename}"))

    def start_download(self):
        if self.download_thread and self.download_thread.is_alive():
            messagebox.showinfo("Download in progress", "A download is already running.")
            return

        url = self.url_var.get().strip()
        output_dir = self.output_dir_var.get().strip()
        playlist_name = self.playlist_name_var.get().strip()
        is_playlist = self.playlist_var.get()
        media_type = self.media_type_var.get()

        if not url:
            messagebox.showerror("Missing URL", "Please enter a YouTube video or playlist URL.")
            return

        if not output_dir:
            messagebox.showerror("Missing output folder", "Please choose where the files should be saved.")
            return

        os.makedirs(output_dir, exist_ok=True)

        self.download_button.configure(state=tk.DISABLED)
        self.progress.start(10)
        self.status_var.set("Starting download...")
        self.log(f"Starting {media_type} download for {'playlist' if is_playlist else 'video'} URL")

        self.download_thread = threading.Thread(
            target=self._download_worker,
            args=(url, output_dir, is_playlist, playlist_name, media_type),
            daemon=True,
        )
        self.download_thread.start()

    def _download_worker(self, url, output_dir, is_playlist, playlist_name, media_type):
        try:
            self.message_queue.put(("status", "Analyzing video and starting download... This may take a moment."))
            options = build_ydl_options(output_dir, is_playlist, playlist_name, media_type, self._progress_hook)
            with yt_dlp.YoutubeDL(options) as downloader:
                downloader.download([url])
            self.message_queue.put(("done", f"Download completed successfully and saved to {output_dir}"))
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
                    self.status_var.set("Done")
                    self._append_log(payload)
                    messagebox.showinfo("Success", payload)
                elif kind == "error":
                    self.progress.stop()
                    self.download_button.configure(state=tk.NORMAL)
                    self.status_var.set("Failed")
                    self._append_log(f"Error: {payload}")
                    messagebox.showerror("Download failed", payload)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self._poll_queue)


def main():
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
