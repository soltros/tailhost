import subprocess
import platform
import os

# Run tailscale status command
output = subprocess.check_output(['tailscale', 'status']).decode('utf-8')

# Parse output to extract IPv4 addresses and hostnames
addresses = {}
for line in output.splitlines():
    if ' IPv4:' in line:
        hostname = line.split()[0]
        ip = line.split('IPv4:')[1].strip()
        addresses[hostname] = ip

# Update hosts file
hosts_file_path = ''
if platform.system() == 'Windows':
    hosts_file_path = r'C:\Windows\System32\drivers\etc\hosts'
elif platform.system() == 'Linux':
    hosts_file_path = '/etc/hosts'

with open(hosts_file_path, 'a') as f:
    for hostname, ip in addresses.items():
        f.write(f'{ip} {hostname}\n')

print('Hosts file updated successfully!')
