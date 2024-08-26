import subprocess
import platform
import os
import ctypes
import sys

def is_admin_windows():
    """Check if the script is running with admin privileges on Windows."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def request_admin_windows():
    """Request admin privileges on Windows."""
    if not is_admin_windows():
        print("Requesting admin privileges...")
        # Re-run the script with admin privileges
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, ' '.join(sys.argv), None, 1)
        exit()

def request_admin_linux():
    """Request admin privileges on Linux."""
    if os.geteuid() != 0:
        print("This script requires root privileges. Re-running with sudo...")
        # Re-run the script with sudo
        subprocess.call(['sudo', sys.executable] + sys.argv)
        exit()

# Request admin privileges based on OS
if platform.system() == 'Windows':
    request_admin_windows()
elif platform.system() == 'Linux':
    request_admin_linux()

# Run tailscale status command
try:
    output = subprocess.check_output(['tailscale', 'status']).decode('utf-8')
except subprocess.CalledProcessError as e:
    print(f"Error running Tailscale command: {e}")
    exit(1)

# Parse output to extract IPv4 addresses and hostnames
addresses = {}
for line in output.splitlines():
    if 'IPv4:' in line:
        parts = line.split()
        hostname = parts[0]
        ip_index = parts.index('IPv4:') + 1
        ip = parts[ip_index]
        addresses[hostname] = ip

# Determine the correct hosts file path
hosts_file_path = ''
if platform.system() == 'Windows':
    hosts_file_path = r'C:\Windows\System32\drivers\etc\hosts'
elif platform.system() in ['Linux', 'Darwin']:  # Darwin for macOS
    hosts_file_path = '/etc/hosts'
else:
    print(f"Unsupported OS: {platform.system()}")
    exit(1)

# Check if script has the necessary permissions
if platform.system() in ['Linux', 'Darwin'] and not os.access(hosts_file_path, os.W_OK):
    print("Permission denied: you need to run this script as root.")
    exit(1)

# Update hosts file
with open(hosts_file_path, 'a+') as f:
    f.seek(0)
    existing_entries = f.read()

    for hostname, ip in addresses.items():
        entry = f'{ip} {hostname}\n'
        if entry not in existing_entries:
            f.write(entry)

print('Hosts file updated successfully!')
