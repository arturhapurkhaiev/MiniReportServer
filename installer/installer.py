import tkinter as tk
from tkinter import ttk
import subprocess
import threading


def run_installer():

    install_btn.config(state="disabled")

    log("Starting MiniSoft Analytics installation...")

    thread = threading.Thread(target=install_process)
    thread.start()


def install_process():

    process = subprocess.Popen(
        ["powershell",
         "-ExecutionPolicy",
         "Bypass",
         "-File",
         "../scripts/install_server.ps1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    for line in process.stdout:
        log(line.strip())

    process.wait()

    if process.returncode == 0:
        log("Installation completed")
        progress["value"] = 100
    else:
        log("Installation failed")


def log(text):

    log_box.insert(tk.END, text + "\n")
    log_box.see(tk.END)

    root.update()


# ------------------------
# GUI
# ------------------------

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
    command=run_installer
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
