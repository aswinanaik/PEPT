import re
import subprocess
import psutil
from datetime import datetime
import sqlite3
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import os
import django

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'privilege_escalation_tool.settings')
django.setup()

# Path to the auth log file
AUTH_LOG = "/var/log/auth.log"

# Database to store warnings
conn = sqlite3.connect('security_monitor.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS warnings
             (id INTEGER PRIMARY KEY, timestamp TEXT, message TEXT)''')
conn.commit()

# Get the Channels layer
channel_layer = get_channel_layer()

def monitor_logs():
    with open(AUTH_LOG, 'r') as logfile:
        logfile.seek(0, 2)  # Go to the end of the file
        while True:
            line = logfile.readline()
            if line:
                # Detect sudo or su usage
                if "sudo:" in line or "su:" in line:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    message = f"Suspicious activity detected: {line.strip()}"
                    print(f"[WARNING] {message}")

                    # Store warning in the database
                    c.execute("INSERT INTO warnings (timestamp, message) VALUES (?, ?)", (timestamp, message))
                    conn.commit()

                    # Send real-time update to the dashboard
                    async_to_sync(channel_layer.group_send)(
                        "dashboard",
                        {
                            "type": "send.update",
                            "message": message,
                        }
                    )

if __name__ == "__main__":
    monitor_logs()
