import psutil
import socket

# -------------------------------
# CONFIGURATION
# -------------------------------
# Define a whitelist of allowed ports (adjust as needed)
print("Traffic Coop started")
WHITELIST_PORTS = {22, 80, 443, 3306}  # Example: SSH, HTTP, HTTPS, MySQL

def get_open_ports():
    """
    Retrieves all open network ports with their PID and username.
    Returns a list of dictionaries with port, pid, username, and process name.
    """
    open_ports = []

    try:
        # psutil.net_connections(kind='inet') covers TCP/UDP IPv4 & IPv6
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == psutil.CONN_LISTEN:  # Only listening ports
                laddr = conn.laddr
                port = laddr.port
                pid = conn.pid

                if pid is not None:
                    try:
                        proc = psutil.Process(pid)
                        username = proc.username()
                        pname = proc.name()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        username = "N/A"
                        pname = "N/A"
                else:
                    username = "N/A"
                    pname = "N/A"

                open_ports.append({
                    "port": port,
                    "pid": pid,
                    "username": username,
                    "process": pname
                })

    except Exception as e:
        print(f"[ERROR] Failed to retrieve open ports: {e}")

    return open_ports


def main():
    open_ports = get_open_ports()

    if not open_ports:
        print("No open listening ports found.")
        return

    print("\n=== Open Ports on This Machine ===")
    for entry in open_ports:
        print(f"Port: {entry['port']:<5} | PID: {entry['pid']:<6} | "
              f"User: {entry['username']:<15} | Process: {entry['process']}")

    # Identify suspicious ports
    suspicious = [p for p in open_ports if p['port'] not in WHITELIST_PORTS]

    print("\n=== Suspicious Ports (Not in Whitelist) ===")
    if suspicious:
        for entry in suspicious:
            print(f"[!] Port: {entry['port']} | PID: {entry['pid']} | "
                  f"User: {entry['username']} | Process: {entry['process']}")
    else:
        print("No suspicious ports detected.")

if __name__ == "__main__":
    main()