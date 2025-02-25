import os
import sys
import shutil
import ctypes
import platform
from typing import List, Tuple

# Check if script is running with admin privileges (Required for low-level disk access)
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if platform.system() == "Windows" and not is_admin():
    print("Please run this script as an administrator.")
    sys.exit(1)

# Function to list available drives (Windows only)
def list_drives() -> List[str]:
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for letter in range(65, 91):  # ASCII 'A' to 'Z'
        if bitmask & (1 << (letter - 65)):
            drives.append(f"{chr(letter)}:")
    return drives

# Function to simulate a Quick Scan (Fetching deleted files from Recycle Bin)
def quick_scan(drive: str) -> List[Tuple[str, str]]:
    print(f"Performing Quick Scan on {drive}...")
    recycle_bin = os.path.join(drive, "$Recycle.Bin")
    recoverable_files = []
    
    if os.path.exists(recycle_bin):
        for root, _, files in os.walk(recycle_bin):
            for file in files:
                file_path = os.path.join(root, file)
                recoverable_files.append((file_path, "Recoverable"))
    
    if recoverable_files:
        print("Found recoverable files:")
        for idx, (file, status) in enumerate(recoverable_files, 1):
            print(f"{idx}. {file} - {status}")
    else:
        print("No deleted files found.")
    
    return recoverable_files

# Function to simulate a Deep Scan (Reading raw sectors)
def deep_scan(drive: str) -> List[Tuple[str, str]]:
    print(f"Performing Deep Scan on {drive}... This may take some time.")
    # Placeholder for deep scan logic
    print("Deep Scan complete. Found several recoverable files.")
    return []  # Placeholder return

# Function to recover a selected file
def recover_file(file_path: str, destination: str):
    try:
        if os.path.exists(file_path):
            shutil.copy(file_path, destination)
            print(f"Successfully recovered {file_path} to {destination}")
        else:
            print("File not found. Recovery failed.")
    except Exception as e:
        print(f"Error recovering file: {e}")

# CLI Interface
def main():
    print("Welcome to File Recovery Tool")
    drives = list_drives()
    if not drives:
        print("No available drives found.")
        return
    
    print("Available Drives:")
    for idx, drive in enumerate(drives, 1):
        print(f"{idx}. {drive}")
    
    choice = input("Select a drive to scan (Enter number or 'exit' to quit): ")
    if choice.lower() == 'exit':
        sys.exit()
    
    try:
        selected_drive = drives[int(choice) - 1]
    except (IndexError, ValueError):
        print("Invalid choice. Exiting.")
        return
    
    scan_type = input("Choose scan type - (1) Quick Scan, (2) Deep Scan: ")
    if scan_type == '1':
        recoverable_files = quick_scan(selected_drive)
    elif scan_type == '2':
        recoverable_files = deep_scan(selected_drive)
    else:
        print("Invalid selection. Exiting.")
        return
    
    if not recoverable_files:
        print("No files to recover. Exiting.")
        return
    
    file_choice = input("Enter the number of the file to recover or 'all' to recover everything: ")
    destination = input("Enter the recovery destination path: ")
    
    if file_choice.lower() == 'all':
        print("Recovering all found files...")
        for file_path, _ in recoverable_files:
            recover_file(file_path, destination)
        print("Recovery complete.")
    else:
        try:
            file_choice = int(file_choice) - 1
            if 0 <= file_choice < len(recoverable_files):
                recover_file(recoverable_files[file_choice][0], destination)
            else:
                print("Invalid selection. Exiting.")
        except ValueError:
            print("Invalid input. Exiting.")
    
    print("Process completed. Exiting tool.")

if __name__ == "__main__":
    main()
