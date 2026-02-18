#Real - Time Detection and Prevention of Suspsious Network Connections
#if ip conncetions 3 times -- considering suspisous
''' Problem Statement-
A server can become slow or unresponsive when a single IP address makes repeated connection attempts to its ports, 
which may indicate brute-force attacks or connection flooding. Manual monitoring cannot detect such threats in real time. 
Therefore, an automated system is needed to monitor active network connections, identify suspicious IP activity, and alert
administrators when abnormal connection patterns occur. This helps improve server security, stability, and threat response time.
'''

import subprocess
import time

from collections import Counter

THRESHOLD = 5

CHECK_INTERVAL = 3

print("Real-time IP monitor started...")

while True:
    output = subprocess.getoutput("netstat -n")

    ips = []

    for line in output.splitlines():
        parts = line.split()

        if len(parts) >= 3 and "." in parts[2]:
             ip = parts[2].split(":")[0]

             ips.append(ip)

    counts = Counter(ips)

    for ip, count in counts.items():
        if count > THRESHOLD:
            print(f" Suspicious IP detected: {ip} ({count} connections)")

    time.sleep(CHECK_INTERVAL)
  