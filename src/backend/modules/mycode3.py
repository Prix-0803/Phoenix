import os
import shutil
import platform
import pyfiglet

def banner():
    ascii_banner = pyfiglet.figlet_format("Data Recovery Tool")
    print(ascii_banner)

def get_storage_devices():
    """Detects all connected storage devices (Internal + External)"""
    system = platform.system()
    drives = []
    
    if system == "Windows":
        import string
        from ctypes import windll

        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                drives.append(f"{letter}:\\")
            bitmask >>= 1

    elif system == "Darwin":  # macOS
        drives = ["/Volumes/" + d for d in os.listdir("/Volumes")]

    return drives

def scan_deleted_files(directory):
    """Scans for potentially deleted/corrupted files"""
    recovered_files = []

    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if os.access(file_path, os.R_OK):  # Check if file is readable
                recovered_files.append(file_path)
            else:
                print(f"[-] Skipping (Permission Denied): {file_path}")

    return recovered_files

def recover_files(files, recovery_path):
    """Attempts to recover files to a new location"""
    if not os.path.exists(recovery_path):
        try:
            os.makedirs(recovery_path)
        except PermissionError:
            print("[-] ERROR: Permission denied while creating recovery folder!")
            return
    
    recovered_count = 0
    for file in files:
        try:
            shutil.copy(file, recovery_path)
            print(f"[+] Recovered: {file}")
            recovered_count += 1
        except PermissionError:
            print(f"[-] Permission Denied: {file}")
        except Exception as e:
            print(f"[-] Failed to recover: {file} | Error: {str(e)}")
    
    print(f"\n✅ Recovery Process Completed! Successfully recovered {recovered_count} files. ✅\n")

def main():
    while True:
        banner()
        print("Scanning for storage devices...\n")
        
        devices = get_storage_devices()
        if not devices:
            print("No storage devices found!")
            return
        
        print("Detected Storage Devices:")
        for idx, device in enumerate(devices, 1):
            print(f"{idx}. {device}")

        choice = input("\nSelect a storage device to scan (Enter Number or 'exit' to quit): ")
        if choice.lower() == "exit":
            print("Exiting Data Recovery Tool. Goodbye!")
            break

        if not choice.isdigit() or int(choice) - 1 >= len(devices):
            print("Invalid choice! Please enter a valid number.")
            continue

        target_device = devices[int(choice) - 1]
        print(f"\nScanning {target_device} for deleted/corrupted files...\n")
        
        deleted_files = scan_deleted_files(target_device)
        
        if not deleted_files:
            print("No deleted/corrupted files found!")
            continue

        print(f"Found {len(deleted_files)} deleted/corrupted files.")
        recovery_location = input("Enter recovery folder path (e.g., C:\\Recovered or /Users/Recovered): ")

        recover_files(deleted_files, recovery_location)
        
        restart = input("Press Enter to start a new scan or type 'exit' to quit: ")
        if restart.lower() == "exit":
            break

if __name__ == "__main__":
    main()
