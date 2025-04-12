import re
import psutil
from datetime import datetime
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import os
import django
import time

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'privilege_escalation_tool.settings')
django.setup()

from monitor.models import Warning  # Import the Warning model

# Paths to log files
AUTH_LOG = "/var/log/auth.log"
KERNEL_LOG = "/var/log/kern.log"

# Get the Channels layer
channel_layer = get_channel_layer()

# Patterns for privilege escalation detection
ESCALATION_PATTERNS = [
    r'sudo:',
    r'su:',
    r'pkexec',
    r'polkitd',
    r'PAM.*authentication failure',
    r'authentication failure',
    r'new group:.*\(root\)',
    r'useradd.*root',
    r'passwd.*root',
    r'changed UID to 0',
    r'setuid',
    r'cap_setuid',
    r'sudoers',
    r'/etc/shadow',
]

# Patterns for kernel-level privilege escalation detection
KERNEL_ESCALATION_PATTERNS = [
    r'insmod',  # Insert kernel module
    r'modprobe',  # Load kernel module
    r'rmmod',  # Remove kernel module
    r'capsh',  # Manipulate capabilities
    r'setcap',  # Set file capabilities
    r'/proc/sys',  # Modify kernel parameters
    r'/sys/kernel',  # Modify kernel settings
    r'kernel:.*BUG',  # Kernel bug messages
    r'kernel:.*Oops',  # Kernel oops messages
    r'kernel:.*panic',  # Kernel panic messages
]


def detect_escalation(line, patterns):
    """Detect privilege escalation patterns in log lines."""
    for pattern in patterns:
        if re.search(pattern, line, re.IGNORECASE):
            return True
    return False


def monitor_logs():
    """Monitor auth logs for suspicious activity."""
    with open(AUTH_LOG, 'r') as logfile:
        logfile.seek(0, 2)  # Go to the end of the file
        while True:
            line = logfile.readline()
            if not line:
                time.sleep(0.2)
                continue

            if detect_escalation(line, ESCALATION_PATTERNS):
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                message = f"Suspicious activity detected: {line.strip()}"
                handle_privilege_escalation(message, "Auth Log")


def monitor_kernel_logs():
    """Monitor kernel logs for suspicious activity."""
    with open(KERNEL_LOG, 'r') as logfile:
        logfile.seek(0, 2)  # Go to the end of the file
        while True:
            line = logfile.readline()
            if not line:
                time.sleep(0.2)
                continue

            if detect_escalation(line, KERNEL_ESCALATION_PATTERNS):
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                message = f"Kernel-level suspicious activity detected: {line.strip()}"
                handle_privilege_escalation(message, "Kernel Log")


def monitor_processes():
    """Monitor running processes for privilege escalation attempts."""
    suspicious_processes = ["capsh", "setcap", "insmod", "modprobe", "rmmod"]
    while True:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = " ".join(proc.info['cmdline']) if proc.info['cmdline'] else ""
                for suspicious in suspicious_processes:
                    if suspicious in cmdline:
                        message = f"Suspicious process detected: {cmdline} (PID: {proc.info['pid']})"
                        handle_privilege_escalation(message, "Process Monitor")
                        proc.terminate()  # Terminate the suspicious process
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        time.sleep(0.2)


def handle_privilege_escalation(message, source):
    """Handle detected privilege escalation attempts."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{source}] {message}"
    print(f"[WARNING] {full_message}")

    # Store warning in the database using Django ORM
    Warning.objects.create(message=full_message)

    # Send real-time update to the dashboard
    async_to_sync(channel_layer.group_send)(
        "dashboard",
        {
            "type": "send.update",
            "message": full_message,
        }
    )


if __name__ == "__main__":
    import threading

    # Start monitoring logs and processes in parallel
    auth_log_thread = threading.Thread(target=monitor_logs, daemon=True)
    kernel_log_thread = threading.Thread(target=monitor_kernel_logs, daemon=True)
    process_thread = threading.Thread(target=monitor_processes, daemon=True)

    auth_log_thread.start()
    kernel_log_thread.start()
    process_thread.start()

    auth_log_thread.join()
    kernel_log_thread.join()
    process_thread.join()