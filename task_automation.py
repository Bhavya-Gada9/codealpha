import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import time
import matplotlib.pyplot as plt

# -----------------------------
# Global variables
# -----------------------------
src_path = None
dest_path = None
last_moved_types = {}
window = None
message_label = None
progress_bar = None

# -----------------------------
# Move image files
# -----------------------------
def move_image_files():
    process_images(shutil.move, "Moved")

# -----------------------------
# Copy image files
# -----------------------------
def copy_image_files():
    process_images(shutil.copy2, "Copied")

# -----------------------------
# Shared process function
# -----------------------------
def process_images(action_func, action_name):
    src = src_path.get().strip()
    dest = dest_path.get().strip()

    if not src or not dest:
        message_label.config(text="⚠ Please select both folders!", fg="red")
        return

    if not os.path.exists(src):
        message_label.config(text="⚠ Source folder does not exist!", fg="red")
        return

    if not os.path.exists(dest):
        os.makedirs(dest)

    img_files = [f for f in os.listdir(src) if f.strip().lower().endswith(('.jpg', '.png'))]

    if not img_files:
        message_label.config(text=f"ℹ No JPG/PNG files found in source!", fg="blue")
        return

    total_files = len(img_files)
    processed_count = 0
    jpg_count = 0
    png_count = 0
    progress_bar["value"] = 0
    window.update_idletasks()

    for i, file in enumerate(img_files, start=1):
        src_file = os.path.join(src, file)
        dest_file = os.path.join(dest, file)
        try:
            action_func(src_file, dest_file)
            processed_count += 1
            if file.lower().endswith('.jpg'):
                jpg_count += 1
            else:
                png_count += 1
            message_label.config(text=f"{action_name}: {file}", fg="green")
            window.update_idletasks()
            time.sleep(0.05)
        except Exception as e:
            message_label.config(text=f"Error {action_name.lower()} {file}: {e}", fg="red")
        progress_bar["value"] = (i / total_files) * 100
        window.update_idletasks()

    message_label.config(text=f"✅ {processed_count}/{total_files} files {action_name.lower()}!", fg="green")
    log_action(img_files, src, dest, action_name)

    # Enable buttons dynamically
    open_button["state"] = "normal"
    display_log_button["state"] = "normal"
    delete_button["state"] = "normal"
    graph_button["state"] = "normal"

    last_moved_types["jpg"] = jpg_count
    last_moved_types["png"] = png_count

    plot_moved_graph(jpg_count, png_count)

# -----------------------------
# Log action to file
# -----------------------------
def log_action(files, src, dest, action_name):
    with open("operation_log.txt", "a") as log:
        log.write(f"\n--- {action_name} Operation at {datetime.now()} ---\n")
        log.write(f"Source: {src}\nDestination: {dest}\n")
        for f in files:
            log.write(f"[{action_name}] {f}\n")

# -----------------------------
# Display Log
# -----------------------------
def display_log():
    if os.path.exists("operation_log.txt"):
        with open("operation_log.txt", "r") as log:
            content = log.read()
        log_window = tk.Toplevel(window)
        log_window.title("Operation Log")
        log_window.geometry("600x400")
        text_area = tk.Text(log_window, wrap=tk.WORD)
        text_area.pack(expand=True, fill=tk.BOTH)
        text_area.insert(tk.END, content)
    else:
        messagebox.showinfo("Log", "No log file found.")

# -----------------------------
# Delete JPG/PNG files recursively with pie chart
# -----------------------------
def delete_images_recursive():
    folder = filedialog.askdirectory(title="Select Folder to Delete Images Recursively")
    if not folder:
        return

    confirm = messagebox.askyesno(
        "Confirm Delete",
        f"Are you sure you want to delete ALL JPG/PNG files from this folder and all subfolders?\n{folder}"
    )
    if confirm:
        count_deleted = 0
        count_failed = 0
        total_before = 0
        all_files = []

        # Count all JPG/PNG files recursively
        for root, dirs, files in os.walk(folder):
            for f in files:
                if f.strip().lower().endswith(('.jpg', '.png')):
                    total_before += 1
                    all_files.append(os.path.join(root, f))

        # Delete files
        for file_path in all_files:
            try:
                os.remove(file_path)
                count_deleted += 1
            except Exception as e:
                count_failed += 1

        remaining = total_before - count_deleted
        message_label.config(
            text=f"🗑 Deleted {count_deleted} images. Remaining: {remaining}. Failed: {count_failed}",
            fg="red"
        )

        # Log deleted files
        with open("operation_log.txt", "a") as log:
            log.write(f"\n--- Delete Operation at {datetime.now()} ---\n")
            log.write(f"Folder: {folder}\n")
            for f in all_files:
                log.write(f"[Deleted] {f}\n")

        # Show pie chart
        if total_before > 0:
            labels = ['Deleted', 'Remaining']
            sizes = [count_deleted, remaining]
            colors = ['#f44336', '#4caf50']
            plt.figure("Delete Summary")
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.0f%%', startangle=90)
            plt.title("Deleted vs Remaining Images")
            plt.show()
# -----------------------------
# Graph of last moved/copied images
# -----------------------------
def plot_moved_graph(jpg_count, png_count):
    if jpg_count == 0 and png_count == 0:
        messagebox.showinfo("Graph", "No files moved or copied yet.")
        return
    labels = ['JPG', 'PNG']
    sizes = [jpg_count, png_count]
    colors = ['#4caf50', '#2196f3']
    plt.figure("Files Summary")
    plt.bar(labels, sizes, color=colors)
    plt.title("Number of Files Moved/Copied by Type")
    plt.ylabel("Count")
    plt.show()
def show_user_manual():
    manual_text = """
🖼 Interactive Image Manager — User Manual

1. Select Source Folder: Folder containing JPG/PNG images.
2. Select Destination Folder: Folder where images will be moved/copied.
3. Move Images: Moves images from source to destination.
4. Copy Images: Copies images without removing from source.
5. Delete JPG/PNG from Folder: Deletes all images from selected folder and subfolders.
6. Display Log: Shows operation log (Move, Copy, Delete).
7. Show Graph of Files: Displays a bar chart of last moved/copied files.
8. Open Destination Folder: Opens destination folder in Explorer.
9. Clear Log: Clears the operation log.
10. Exit: Closes the application.

✅ Note: Always check the progress bar and messages for operation status.
"""
    manual_window = tk.Toplevel(window)
    manual_window.title("User Manual")
    manual_window.geometry("700x500")
    text_area = tk.Text(manual_window, wrap=tk.WORD, font=("Segoe UI", 11))
    text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
    text_area.insert(tk.END, manual_text)
    text_area.config(state=tk.DISABLED)


# -----------------------------
# Browse folders
# -----------------------------
def browse_source():
    folder = filedialog.askdirectory(title="Select Source Folder")
    if folder:
        src_path.set(folder)

def browse_destination():
    folder = filedialog.askdirectory(title="Select Destination Folder")
    if folder:
        dest_path.set(folder)

# -----------------------------
# Open Destination Folder
# -----------------------------
def open_destination():
    dest = dest_path.get()
    if os.path.exists(dest):
        os.startfile(dest)
    else:
        messagebox.showerror("Error", "Destination folder does not exist!")

# -----------------------------
# Clear Log
# -----------------------------
def clear_log():
    if os.path.exists("operation_log.txt"):
        open("operation_log.txt", "w").close()
    message_label.config(text="Log cleared.", fg="blue")

# -----------------------------
# Exit App
# -----------------------------
def exit_app():
    if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
        window.destroy()

# -----------------------------
# GUI Setup
# -----------------------------
window = tk.Tk()
window.title("🖼 Interactive Image Manager")
window.geometry("950x600")
window.configure(bg="#f0f8ff")
window.state('zoomed')

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=6)
style.configure("TLabel", font=("Segoe UI", 12), background="#f0f8ff")

# Variables
src_path = tk.StringVar()
dest_path = tk.StringVar()
last_moved_types = {}

# Header
header = tk.Label(window, text="📂 Interactive Image Manager", font=("Segoe UI", 20, "bold"),
                  bg="#1976d2", fg="white", pady=15)
header.pack(fill=tk.X)

# Source folder
frame1 = tk.Frame(window, bg="#f0f8ff")
frame1.pack(pady=10)
tk.Label(frame1, text="Source Folder:", bg="#f0f8ff").grid(row=0, column=0, padx=5)
tk.Entry(frame1, textvariable=src_path, width=60).grid(row=0, column=1, padx=5)
ttk.Button(frame1, text="Browse", command=browse_source).grid(row=0, column=2, padx=5)

# Destination folder
frame2 = tk.Frame(window, bg="#f0f8ff")
frame2.pack(pady=10)
tk.Label(frame2, text="Destination Folder:", bg="#f0f8ff").grid(row=0, column=0, padx=5)
tk.Entry(frame2, textvariable=dest_path, width=60).grid(row=0, column=1, padx=5)
ttk.Button(frame2, text="Browse", command=browse_destination).grid(row=0, column=2, padx=5)

# Progress bar
progress_bar = ttk.Progressbar(window, orient="horizontal", length=550, mode="determinate")
progress_bar.pack(pady=20)

# Animated message
message_label = tk.Label(window, text="", font=("Segoe UI", 12), bg="#f0f8ff", fg="green")
message_label.pack(pady=5)

# Buttons frame
button_frame = tk.Frame(window, bg="#f0f8ff")
button_frame.pack(pady=10)

ttk.Button(button_frame, text="Move Images", command=move_image_files).grid(row=0, column=0, padx=10)
ttk.Button(button_frame, text="Copy Images", command=copy_image_files).grid(row=0, column=1, padx=10)
open_button = ttk.Button(button_frame, text="Open Destination Folder", command=open_destination, state="disabled")
open_button.grid(row=0, column=2, padx=10)
display_log_button = ttk.Button(button_frame, text="Display Log", command=display_log, state="disabled")
display_log_button.grid(row=0, column=3, padx=10)
delete_button = ttk.Button(button_frame, text="Delete JPG/PNG from Folder", command=delete_images_recursive, state="disabled")
delete_button.grid(row=0, column=4, padx=10)
graph_button = ttk.Button(button_frame, text="Show Graph of Files",
                          command=lambda: plot_moved_graph(last_moved_types.get("jpg", 0),
                                                          last_moved_types.get("png", 0)),
                          state="disabled")
graph_button.grid(row=0, column=5, padx=10)
ttk.Button(button_frame, text="Clear Log", command=clear_log).grid(row=0, column=6, padx=10)
ttk.Button(button_frame, text="Exit", command=exit_app).grid(row=0, column=7, padx=10)
ttk.Button(button_frame, text="User Manual", command=show_user_manual).grid(row=0, column=8, padx=10)

# Footer
footer = tk.Label(window, text="Developed by Bhavya Gada — Internship Project @CodeAlpha", font=("Segoe UI", 10, "italic"),
                  bg="#f0f8ff", fg="#0d47a1")
footer.pack(side=tk.BOTTOM, pady=8)

window.mainloop()
