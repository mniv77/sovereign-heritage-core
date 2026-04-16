# sovereign_bridge.py (Runs on your LOCAL PC)
# The "Secret Code" Generator: Creates an encrypted tunnel from PC to Server.
# Usage: python sovereign_bridge.py

import os
import subprocess
import time

# --- CONFIGURATION ---
SERVER_USER = "MeirNiv"
SERVER_HOST = "v-MeirNiv.pythonanywhere.com" # Or your specific server IP
LOCAL_DB_PORT = 3306
REMOTE_PIPE_PORT = 3307 # Matches db_config.py

def establish_tunnel():
    """
    Creates a Reverse SSH Tunnel.
    This acts as the 'Secret Code' that opens access ONLY to your server IP.
    """
    # COMMAND EXPLANATION:
    # -R: Remote Port Forwarding (Server:3307 -> PC:3306)
    # -N: Do not execute a remote command (just keep the pipe open)
    # -i: Path to your private SSH key (The 'Physical Key')
    ssh_cmd = [
        "ssh", "-R", f"{REMOTE_PIPE_PORT}:127.0.0.1:{LOCAL_DB_PORT}",
        f"{SERVER_USER}@{SERVER_HOST}",
        "-N",
        "-o", "ServerAliveInterval=60",
        "-o", "ExitOnForwardFailure=yes"
    ]

    print(f"--- SOVEREIGN BRIDGE INITIATED ---")
    print(f"Status: Creating Encrypted Pipe to {SERVER_HOST}...")
    print(f"Security: Local MySQL is now masked behind Remote Port {REMOTE_PIPE_PORT}")
    
    try:
        process = subprocess.Popen(ssh_cmd)
        print("Protocol: ACTIVE. The Server App now has access to the Home Node.")
        print("Note: To lock the database, press Ctrl+C or turn off this PC.")
        process.wait()
    except Exception as e:
        print(f"Bridge Failed: {e}")
        time.sleep(5)

if __name__ == "__main__":
    while True:
        establish_tunnel()
        print("Connection lost. Re-establishing Sovereign Handshake in 5s...")
        time.sleep(5)