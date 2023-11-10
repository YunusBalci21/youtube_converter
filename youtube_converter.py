import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pytube import YouTube
import threading
import os
import subprocess
import platform
from queue import Queue

def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100
    progress_queue.put((percentage_of_completion, bytes_downloaded, total_size))

def on_complete(stream, file_handle):
    complete_queue.put(file_handle)

def update_progress():
    while not progress_queue.empty():
        percentage, bytes_downloaded, total_size = progress_queue.get()
        progress_bar['value'] = percentage
        speed_label.config(text=f"{bytes_downloaded//1024} KB of {total_size//1024} KB downloaded...")
        root.update_idletasks()

    root.after(100, update_progress)

def update_completion():
    while not complete_queue.empty():
        file_path = complete_queue.get()
        download_button.config(state="normal")
        speed_label.config(text="Download completed!")
        progress_bar['value'] = 100
        play_button.config(command=lambda: play_video(file_path), state="normal")
        show_button.config(command=lambda: show_in_folder(file_path), state="normal")

    root.after(100, update_completion)

def download_video():
    download_button.config(state="disabled")
    play_button.config(state="disabled")
    show_button.config(state="disabled")
    video_url = url_entry.get()
    save_path = filedialog.askdirectory()
    if not video_url or not save_path:
        messagebox.showwarning("Warning", "Both URL and Save Path are required!")
        download_button.config(state="normal")
        return

    try:
        yt = YouTube(video_url, on_progress_callback=on_progress, on_complete_callback=on_complete)
        video_stream = yt.streams.get_highest_resolution()
        threading.Thread(target=lambda: video_stream.download(output_path=save_path)).start()
    except Exception as e:
        messagebox.showerror("Error", str(e))
        download_button.config(state="normal")

def play_video(file_path):
    if platform.system() == "Windows":
        os.startfile(file_path)
    elif platform.system() == "Darwin":  # macOS
        subprocess.call(["open", file_path])
    else:  # Linux
        subprocess.call(["xdg-open", file_path])

def show_in_folder(file_path):
    folder_path = os.path.dirname(file_path)
    if platform.system() == "Windows":
        os.startfile(folder_path)
    elif platform.system() == "Darwin":  # macOS
        subprocess.call(["open", folder_path])
    else:  # Linux
        subprocess.call(["xdg-open", folder_path])

# Create the main window
root = tk.Tk()
root.title("YouTube Video Downloader by Y.B.")

# Create the URL entry
url_label = tk.Label(root, text="YouTube Video URL:")
url_label.pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

# Create the download button
download_button = tk.Button(root, text="Download Video", command=download_video)
download_button.pack(pady=20)

# Progress bar widget
progress_bar = ttk.Progressbar(root, orient='horizontal', length=400, mode='determinate')
progress_bar.pack(pady=10)

# Speed label
speed_label = tk.Label(root, text="")
speed_label.pack(pady=5)

# Play video button
play_button = tk.Button(root, text="Play Video", state="disabled")
play_button.pack(side="left", fill="both", expand=True, padx=5, pady=5)

# Show in folder button
show_button = tk.Button(root, text="Show in Folder", state="disabled")
show_button.pack(side="right", fill="both", expand=True, padx=5, pady=5)

# Setup the queues for handling download progress and completion
progress_queue = Queue()
complete_queue = Queue()

# Start the GUI event loop and periodic check functions
root.after(100, update_progress)
root.after(100, update_completion)
root.mainloop()
