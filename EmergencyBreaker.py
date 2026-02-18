'''
Monitors a specific partition’s disk usage.
If usage exceeds 90%, finds the top 5 largest files.
Moves them into a compressed .zip archive on another drive (or /tmp).
Helps prevent a system crash due to full disk.

'''

import os
import shutil
import psutil
import zipfile
import time
from pathlib import Path
print("Emergency breaker started")

PARTITION_PATH = "/"  # Partition to monitor (e.g., "/", "/home", "D:\\")
USAGE_THRESHOLD = 90  # Percentage threshold
ARCHIVE_DEST = "/tmp"  # Destination for the zip archive (must have free space)
CHECK_INTERVAL = 60    # Seconds between checks
TOP_N_FILES = 5        # Number of largest files to move


def get_disk_usage(path):
    """Return disk usage percentage for the given path."""
    usage = psutil.disk_usage(path)
    return usage.percent

def find_largest_files(path, top_n=5):
    """Find the top N largest files in the given path."""
    file_sizes = []
    for root, _, files in os.walk(path):
        for name in files:
            try:
                filepath = os.path.join(root, name)
                size = os.path.getsize(filepath)
                file_sizes.append((filepath, size))
            except (PermissionError, FileNotFoundError):
                continue
    # Sort by size (descending) and return top N
    return sorted(file_sizes, key=lambda x: x[1], reverse=True)[:top_n]

def create_zip_archive(files, archive_path):
    """Create a zip archive containing the given files."""
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path, _ in files:
            try:
                zipf.write(file_path, arcname=os.path.basename(file_path))
            except FileNotFoundError:
                continue

def remove_files(files):
    """Delete the given files from disk."""
    for file_path, _ in files:
        try:
            os.remove(file_path)
        except FileNotFoundError:
            continue

def monitor_disk():
    """Monitor disk usage and take action if threshold exceeded."""
    while True:
        usage_percent = get_disk_usage(PARTITION_PATH)
        print(f"[INFO] Disk usage on {PARTITION_PATH}: {usage_percent:.2f}%")

        if usage_percent >= USAGE_THRESHOLD:
            print(f"[ALERT] Disk usage exceeded {USAGE_THRESHOLD}%!")
            largest_files = find_largest_files(PARTITION_PATH, TOP_N_FILES)

            if not largest_files:
                print("[WARN] No files found to archive.")
                break

            timestamp = time.strftime("%Y%m%d_%H%M%S")
            archive_name = f"disk_cleanup_{timestamp}.zip"
            archive_path = os.path.join(ARCHIVE_DEST, archive_name)

            print(f"[ACTION] Archiving {len(largest_files)} largest files to {archive_path}")
            create_zip_archive(largest_files, archive_path)

            print("[ACTION] Removing original files...")
            remove_files(largest_files)

            print("[DONE] Cleanup completed.")
            break  # Exit after cleanup to avoid repeated deletion

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    # Ensure destination exists
    Path(ARCHIVE_DEST).mkdir(parents=True, exist_ok=True)

    try:
        monitor_disk()
    except KeyboardInterrupt:
        print("\n[EXIT] Monitoring stopped by user.")
    except Exception as e:
        print(f"[ERROR] {e}")

""""
How It Works

Monitors the given partition (PARTITION_PATH) using psutil.
If usage exceeds USAGE_THRESHOLD (90%), it:

Finds the top 5 largest files recursively.
Creates a timestamped .zip archive in ARCHIVE_DEST.
Deletes the original files to free space.


Runs in a loop with a configurable CHECK_INTERVAL.


Requirements
Install dependencies:
Bashpip install psutil


Safety Notes

Run as root/admin if scanning system directories.
Test on a non-critical partition before production use.
Adjust ARCHIVE_DEST to a location with enough free space.
This script moves files by archiving and deleting — ensure backups exist.
"""

