import tkinter as tk
import os
import shutil
import subprocess
import sys

INSTALL_DIR = r"C:\MiniReportServer"

# ------------------------------------------------
# Detect path (works for .py and .exe)
# ------------------------------------------------

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )


# ------------------------------------------------
# LOG
# ------------------------------------------------

def log(msg):

    log_box.insert(tk.END, msg + "\n")
    log_box.see(tk.END)
    root.update()


# ------------------------------------------------
# INSTALL
# ------------------------------------------------

def install():

    install_btn.config(state="disabled")

    log("Starting installation")

    if not os.path.exists(INSTALL_DIR):

        log("Creating installation directory")

        os.makedirs(INSTALL_DIR)

    log("Copying files")

    for item in os.listdir(BASE_DIR):

        if item == "installer":
            continue

        src = os.path.join(BASE_DIR, item)
        dst = os.path.join(INSTALL_DIR, item)

        try:

            if os.path.isdir(src):

                shutil.copytree(src, dst, dirs_exist_ok=True)

            else:

                shutil.copy2(src, dst)

        except Exception as e:

            log(f"Skipped {item}: {e}")

    log("Files copied")

    install_python()

    create_shortcut()

    log("Installation finished")
    log("Run 'MiniSoft Admin' from Desktop")


# ------------------------------------------------
# INSTALL PYTHON LIBRARIES
# ------------------------------------------------

def install_python():

    log("Installing Python libraries")

    subprocess.call([
        "pip",
        "install",
        "-r",
        os.path.join(INSTALL_DIR, "requirements.txt")
    ])


# ------------------------------------------------
# CREATE DESKTOP SHORTCUT
# ------------------------------------------------

def create_shortcut():

    log("Creating desktop shortcut")

    desktop = os.path.join(
        os.path.expanduser("~"),
        "Desktop"
    )

    shortcut = os.path.join(
        desktop,
        "MiniSoft Admin.bat"
    )

    target = r'C:\MiniReportServer\manager\manager.py'

    with open(shortcut, "w") as f:

        f.write(f'python "{target}"')


# ------------------------------------------------
# GUI
# ------------------------------------------------

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
    text="This wizard installs MiniSoft Reporting Server"
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

log_box = tk.Text(root, height=10)

log_box.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=20
)

root.mainloop()
