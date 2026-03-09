import tkinter as tk
from tkinter import ttk
import os
import shutil
import sys

INSTALL_DIR = r"C:\MiniReportServer"


def log(msg):
    log_box.insert(tk.END, msg + "\n")
    log_box.see(tk.END)
    root.update()


def install():

    install_btn.config(state="disabled")

    source_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    log("Creating installation directory")

    os.makedirs(INSTALL_DIR, exist_ok=True)

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

    create_shortcuts()

    log("Installation completed")
    log("Run 'MiniSoft Admin' from Desktop")


def create_shortcuts():

    desktop = os.path.join(os.path.expanduser("~"), "Desktop")

    admin = os.path.join(desktop, "MiniSoft Admin.bat")

    with open(admin, "w") as f:
        f.write(
            'python "C:\\MiniReportServer\\manager\\manager.py"'
        )


# GUI

root = tk.Tk()
root.title("MiniSoft Analytics Installer")
root.geometry("500x400")

title = tk.Label(
    root,
    text="MiniSoft Analytics Platform",
    font=("Arial",16)
)

title.pack(pady=20)

desc = tk.Label(
    root,
    text="This wizard installs MiniSoft Reporting Server",
)

desc.pack(pady=10)

install_btn = tk.Button(
    root,
    text="Install",
    width=20,
    height=2,
    command=install
)

install_btn.pack(pady=20)

log_box = tk.Text(root,height=10)
log_box.pack(fill="both",expand=True,padx=20,pady=20)

root.mainloop()
