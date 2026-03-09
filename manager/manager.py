import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import tkinter.simpledialog as simpledialog

import concurrent.futures
import pyodbc
import socket
import psutil
import json
import os
import subprocess
import webbrowser
import sys

PORT = 1433

stores = []

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(BASE_DIR, "..", "config", "stores.json")
ENV_FILE = os.path.join(BASE_DIR, "..", "config", "credentials.env")
ADMIN_FILE = os.path.join(BASE_DIR, "..", "config", "admin.env")

SQL_USER = ""
SQL_PASS = ""


# -------------------------
# ADMIN LOGIN
# -------------------------

def load_admin_password():

    try:
        with open(ADMIN_FILE) as f:
            for line in f:
                if line.startswith("ADMIN_PASSWORD"):
                    return line.strip().split("=")[1]
    except:
        return None


def admin_login():

    password = load_admin_password()

    root = tk.Tk()
    root.withdraw()

    entered = simpledialog.askstring(
        "MiniSoft Admin",
        "Enter admin password:",
        show="*"
    )

    if entered != password:

        messagebox.showerror(
            "Access denied",
            "Wrong password"
        )

        sys.exit()

    root.destroy()


# -------------------------
# LOG
# -------------------------

def log(msg):

    log_box.insert(tk.END, msg + "\n")
    log_box.see(tk.END)
    root.update()


# -------------------------
# Detect VPN network
# -------------------------

def get_wireguard_network():

    interfaces = psutil.net_if_addrs()

    for name, addrs in interfaces.items():

        if name.lower() == "dwh-vpn":

            for addr in addrs:

                if addr.family == socket.AF_INET:

                    ip = addr.address
                    network = ".".join(ip.split(".")[:3]) + "."
                    return network

    return None


# -------------------------
# Port scan
# -------------------------

def check_port(ip):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.3)

    try:

        s.connect((ip, PORT))
        s.close()
        return ip

    except:

        return None


# -------------------------
# Read MSSQL info
# -------------------------

def get_store_info(ip):

    results = []

    try:

        conn = pyodbc.connect(
            f"DRIVER={{SQL Server}};"
            f"SERVER={ip},1433;"
            f"UID={SQL_USER};"
            f"PWD={SQL_PASS};",
            timeout=1
        )

        cursor = conn.cursor()

        cursor.execute("""
        SELECT name
        FROM master..sysdatabases
        WHERE name LIKE 'minisoft%'
        """)

        databases = [row[0] for row in cursor.fetchall()]

        conn.close()

        for db in databases:

            try:

                conn = pyodbc.connect(
                    f"DRIVER={{SQL Server}};"
                    f"SERVER={ip},1433;"
                    f"DATABASE={db};"
                    f"UID={SQL_USER};"
                    f"PWD={SQL_PASS};",
                    timeout=1
                )

                cursor = conn.cursor()

                cursor.execute("""
                SELECT paramname,paramvalue
                FROM dbo.param
                WHERE paramname IN ('version','magazinname')
                """)

                name = "unknown"
                version = "unknown"

                for row in cursor.fetchall():

                    if row.paramname.lower() == "magazinname":
                        name = row.paramvalue

                    if row.paramname.lower() == "version":
                        version = row.paramvalue

                conn.close()

                results.append((ip, db, name, version))

            except:
                pass

    except:
        pass

    return results


# -------------------------
# Toggle checkbox
# -------------------------

def toggle_check(event):

    item = tree.identify_row(event.y)

    if not item:
        return

    values = list(tree.item(item, "values"))

    if values[0] == "☐":
        values[0] = "☑"
    else:
        values[0] = "☐"

    tree.item(item, values=values)


# -------------------------
# Scan network
# -------------------------

def scan_network():

    global SQL_USER, SQL_PASS

    SQL_USER = sql_user_entry.get()
    SQL_PASS = sql_pass_entry.get()

    if not SQL_USER or not SQL_PASS:

        log("Enter SQL credentials")
        return

    network = get_wireguard_network()

    if network is None:

        status_label.config(text="WireGuard dwh-vpn not connected")
        return

    log(f"Scanning network {network}0/24")

    ips = [network + str(i) for i in range(1, 255)]

    with concurrent.futures.ThreadPoolExecutor(max_workers=120) as executor:

        open_ports = list(filter(None, executor.map(check_port, ips)))

    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=60) as executor:

        for r in executor.map(get_store_info, open_ports):

            if r:
                results.extend(r)

    tree.delete(*tree.get_children())
    stores.clear()

    for ip, db, name, version in results:

        stores.append((ip, db, name, version))

        tree.insert(
            "",
            "end",
            values=("☐", ip, db, name, version)
        )

    log(f"Found {len(stores)} stores")

    status_label.config(text=f"{len(stores)} stores found")


# -------------------------
# Get selected
# -------------------------

def get_selected():

    selected = []

    for item in tree.get_children():

        values = tree.item(item, "values")

        if values[0] == "☑":
            selected.append(values)

    return selected


# -------------------------
# Save config
# -------------------------

def save_config(selected):

    os.makedirs(os.path.join(BASE_DIR, "..", "config"), exist_ok=True)

    stores_json = []

    for values in selected:

        stores_json.append({
            "host": values[1],
            "database": values[2],
            "name": values[3],
            "version": values[4]
        })

    data = {"stores": stores_json}

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    with open(ENV_FILE, "w") as f:

        f.write(f"MSSQL_USER={SQL_USER}\n")
        f.write(f"MSSQL_PASS={SQL_PASS}\n")

    log("Configuration saved")


# -------------------------
# Generate config
# -------------------------

def install_selected():

    selected = get_selected()

    if not selected:

        log("No stores selected")
        return

    save_config(selected)

    log("Config ready for installer")
    status_label.config(text="Config generated")


# -------------------------
# Install server
# -------------------------

def install_server():

    log("Starting server installation")

    subprocess.Popen(
        ["powershell",
         "-ExecutionPolicy", "Bypass",
         "-File", "../scripts/install_server.ps1"]
    )

    status_label.config(text="Installer started")


# -------------------------
# Rebuild DWH
# -------------------------

def rebuild_dwh():

    log("Starting DWH rebuild")

    subprocess.Popen(
        ["wsl", "-d", "Ubuntu",
         "bash", "-c", "cd /opt/dwh && make rebuild"]
    )

    status_label.config(text="Rebuild started")


# -------------------------
# Open reports
# -------------------------

def open_reports():

    webbrowser.open("http://localhost:3000")


# -------------------------
# START
# -------------------------

admin_login()

root = tk.Tk()
root.title("MiniSoft Analytics Control Center")
root.geometry("950x720")

title = tk.Label(root, text="MiniSoft Analytics Control Center", font=("Arial", 14))
title.pack(pady=10)


cred_frame = tk.Frame(root)
cred_frame.pack(pady=10)

tk.Label(cred_frame, text="SQL Login").grid(row=0, column=0)

sql_user_entry = tk.Entry(cred_frame, width=20)
sql_user_entry.grid(row=0, column=1)

tk.Label(cred_frame, text="SQL Password").grid(row=1, column=0)

sql_pass_entry = tk.Entry(cred_frame, show="*", width=20)
sql_pass_entry.grid(row=1, column=1)


scan_btn = tk.Button(root, text="Scan VPN network", width=20, command=scan_network)
scan_btn.pack(pady=10)


columns = ("check", "ip", "db", "store", "version")

tree = ttk.Treeview(root, columns=columns, show="headings")

tree.heading("check", text="")
tree.heading("ip", text="Server IP")
tree.heading("db", text="Database")
tree.heading("store", text="Store name")
tree.heading("version", text="Version")

tree.column("check", width=40, anchor="center")
tree.column("ip", width=150)
tree.column("db", width=160)
tree.column("store", width=420)
tree.column("version", width=80)

tree.pack(fill="both", expand=True, pady=10)

tree.bind("<Button-1>", toggle_check)


install_btn = tk.Button(root, text="Generate config", width=25, command=install_selected)
install_btn.pack(pady=5)

install_server_btn = tk.Button(root, text="Install / Update Server", width=25, command=install_server)
install_server_btn.pack(pady=5)

rebuild_btn = tk.Button(root, text="Rebuild DWH", width=25, command=rebuild_dwh)
rebuild_btn.pack(pady=5)

reports_btn = tk.Button(root, text="Open Reports", width=25, command=open_reports)
reports_btn.pack(pady=5)


log_box = tk.Text(root, height=12)
log_box.pack(fill="both", padx=10, pady=10)


status_label = tk.Label(root, text="Idle")
status_label.pack(pady=10)


root.mainloop()
