import os
import requests
from time import sleep
from datetime import datetime

# Konfiguration
LOG_FILES_UBUNTU = [
    "/var/log/syslog",
    "/var/log/auth.log",
    "/var/log/kern.log",
    "/var/log/ufw.log",
    "/var/log/nginx/access.log",
    "/var/log/nginx/error.log",
    "/var/log/apache2/access.log",
    "/var/log/apache2/error.log",
    "/var/log/fail2ban.log",
    "/var/log/dmesg"
]
LOG_FILES_MAC = ["test.log"]
LOG_FILES_MAC2 = [
    "/var/log/system.log",                
    "/var/log/authd.log",                 
    "/var/log/install.log",               
    "/private/var/log/kernel.log",        
    "/var/log/powermanagement.log",       
    "/private/var/log/com.apple.xpc.launchd.log",  
    "/var/log/pf.log",
    "/var/log/opendirectoryd.log",
    "~/Library/Logs"
]
SERVER_HOST = "192.168.178.26"
SERVER_PORT = 3000
SERVER_URL = f"http://{SERVER_HOST}:{SERVER_PORT}/logs"
CHECK_INTERVAL = 10  # Sekunden zwischen den Checks

current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
logs_directory = os.path.join(parent_directory, "logs")
os.makedirs(logs_directory, exist_ok=True)# Sicherstellen, dass der Logs-Ordner existiert
LOG_FILE = os.path.join(logs_directory, f"agent_{datetime.now().strftime('%Y-%m-%d')}.log")

# Log-Funktion für den Agent
def LOGGER(info, message):
    timestamp = datetime.now()
    log_message = f"[{timestamp}] {info} {message}\n"
    with open(LOG_FILE, "a") as log_file:
        log_file.write(log_message)

# Funktion, um neue Zeilen aus einer Log-Datei zu lesen und direkt zu senden
def tail_and_send(file_path, last_position):
    try:
        with open(file_path, "r") as file:
            # Beim ersten Start Datei-Zeiger ans Ende setzen
            if last_position == 0:
                file.seek(0, 2)  # Gehe zum Ende der Datei
                last_position = file.tell()
                LOGGER("INFO", f"Erster Start: Datei {file_path} zum Ende verschoben.")

            # Lese neue Zeilen
            file.seek(last_position)
            new_lines = file.readlines()
            new_position = file.tell()

            # Verarbeite jede neue Zeile
            for line in new_lines:
                if line.strip():  # Leere Zeilen überspringen
                    send_log_to_server(file_path, line.strip())

            return new_position  # Neue Position zurückgeben
    except Exception as e:
        LOGGER("ERROR", f"Fehler beim Lesen der Datei {file_path}: {e}")
        return last_position

# Funktion, um eine Log-Zeile als JSON zu senden
def send_log_to_server(file_path, log_line):
    log_data = {
        "file": os.path.basename(file_path),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "line": log_line
    }
    try:
        response = requests.post(SERVER_URL, json=log_data)
        if response.status_code in [200, 201]:
            LOGGER("INFO", f"Erfolgreich gesendet: {log_data}")
        else:
            print(log_data)
            LOGGER("ERROR", f"Fehler beim Senden: {response.status_code} - {response.text}")
    except Exception as e:
        LOGGER("ERROR", f"Netzwerkfehler beim Senden: {e}")

# Hauptfunktion des Agents
def main():
    last_positions = {file: 0 for file in LOG_FILES_MAC}  # Speichert die letzte Position jeder Datei
    while True:
        for log_file in LOG_FILES_MAC:
            if os.path.exists(log_file):
                last_positions[log_file] = tail_and_send(log_file, last_positions[log_file])
            #else:
                #LOGGER("ERROR", f"Log-Datei nicht gefunden: {log_file}")
        sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        print("SIEM-Agent gestartet...")
        LOGGER("main", "SIEM-Agent wird gestartet.")
        main()
    except KeyboardInterrupt:
        print("SIEM-Agent gestoppt...")
        LOGGER("main", "SIEM-Agent gestoppt.")
