import tkinter as tk
from tkinter import ttk
import subprocess
import threading
import shutil
import os
import sys

INSTALL_DIR = r"C:\MiniReportServer"


def log(text):

    log_box.insert(tk.END, text + "\n")
    log_box.see(tk.END)

    root.update()


def install():

    install_btn.config(state="disabled")

    thread = threading.Thread(target=install_process)
    thread.start()


def install_process():

    log("Starting MiniSoft Analytics installation")

    source_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    if not os.path.exists(INSTALL_DIR):

        log("Creating installation directory")

        os.makedirs(INSTALL_DIR)

    log("Copying files")

    for item in os.listdir(source_dir):

        if item == "installer":
            continue

        s = os.path.join(source_dir, item)
        d = os.path.join(INSTALL_DIR, item)

        if os.path.isdir(s):

            shutil.copytree(s, d, dirs_exist_ok=True)

        else:

            shutil.copy2(s, d)

    log("Files copied")

    progress["value"] = 20

    log("Installing Python dependencies")

    subprocess.call(
        ["pip", "install", "-r", os.path.join(INSTALL_DIR, "requirements.txt")]
    )

    progress["value"] = 40

    log("Running server installer")

    subprocess.call([
        "powershell",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        os.path.join(INSTALL_DIR, "scripts", "install_server.ps1")
    ])

    progress["value"] = 80

    create_shortcut()

    progress["value"] = 100

    log("Installation completed")

    log("Open reports: http://localhost:3000")


def create_shortcut():

    log("Creating desktop shortcut")

    desktop = os.path.join(os.path.expanduser("~"), "Desktop")

    shortcut = os.path.join(desktop, "MiniSoft Admin.bat")

    target = os.path.join(INSTALL_DIR, "manager", "manager.py")

    with open(shortcut, "w") as f:

        f.write(f'python "{target}"')


# -------------------------
# GUI
# -------------------------

root = tk.Tk()
root.title("MiniSoft Analytics Installer")
root.geometry("600x500")

title = tk.Label(
    root,
    text="MiniSoft Analytics Platform",
    font=("Arial",16)
)

title.pack(pady=20)

desc = tk.Label(
    root,
    text="This wizard will install the MiniSoft Reporting Server\n\nComponents:\n\n• PostgreSQL Data Warehouse\n• Metabase BI Platform\n• Data Pipelines",
    justify="left"
)

desc.pack(pady=10)


install_btn = tk.Button(
    root,
    text="Install Server",
    width=20,
    height=2,
    command=install
)

install_btn.pack(pady=20)


progress = ttk.Progressbar(
    root,
    orient="horizontal",
    length=400,
    mode="determinate"
)

progress.pack(pady=10)


log_box = tk.Text(root, height=15)

log_box.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=20
)

root.mainloop()
