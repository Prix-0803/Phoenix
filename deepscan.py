#!/usr/bin/python3

import pytsk3
import pyewf
import os
import argparse

# Function to open a disk image or live disk
def open_image(image_path, is_live_disk=False):
    if is_live_disk:
        return pytsk3.Img_Info(image_path)
    else:
        ewf_handle = pyewf.handle()
        ewf_handle.open(image_path)
        return pytsk3.Img_Info(ewf_handle)

# Function to extract files from the file system
def extract_file(filesystem, file_entry, output_path):
    with open(output_path, 'wb') as f:
        file_size = file_entry.info.meta.size
        offset = 0
        size = 1024 * 1024  # Read in chunks of 1MB
        while offset < file_size:
            available_to_read = min(size, file_size - offset)
            file_data = file_entry.read_random(offset, available_to_read)
            if not file_data:
                break
            f.write(file_data)
            offset += len(file_data)
    return output_path

# Function to traverse directories, including unallocated and deleted files
def traverse_directory(filesystem, directory, output_dir, recover_unallocated=True):
    recovered_files = []
    for entry in directory:
        if entry.info.name.name in [b'.', b'..']:
            continue
        try:
            f_type = entry.info.meta.type
            if f_type == pytsk3.TSK_FS_META_TYPE_DIR:
                sub_directory = entry.as_directory()
                recovered_files.extend(traverse_directory(filesystem, sub_directory, output_dir, recover_unallocated))
            elif f_type == pytsk3.TSK_FS_META_TYPE_REG:
                if recover_unallocated or not (entry.info.meta.flags & pytsk3.TSK_FS_META_FLAG_UNALLOC):
                    file_name = entry.info.name.name.decode(errors='ignore')
                    output_path = os.path.join(output_dir, file_name)
                    recovered_file = extract_file(filesystem, entry, output_path)
                    recovered_files.append(recovered_file)
        except AttributeError:
            pass
    return recovered_files

# Function to recover files from a live disk or disk image
def recover_files(image_path, output_dir, is_live_disk=False):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    img_info = open_image(image_path, is_live_disk)
    filesystem = pytsk3.FS_Info(img_info)
    root_directory = filesystem.open_dir('/')
    return traverse_directory(filesystem, root_directory, output_dir, recover_unallocated=True)

# Main function to handle user input and recovery process
def main():
    print("Select mode (1: Live Disk Recovery, 2: Disk Image Recovery): ")
    mode = input().strip()
    output_dir = input("Enter output directory to save recovered files: ").strip()

    if mode == '1':
        disk_path = input("Enter the live disk path (e.g., /dev/sda or \\.\\C:): ").strip()
        recovered_files = recover_files(disk_path, output_dir, is_live_disk=True)
    elif mode == '2':
        image_path = input("Enter disk image path: ").strip()
        recovered_files = recover_files(image_path, output_dir, is_live_disk=False)
    else:
        print("Invalid mode selected.")
        return

    if recovered_files:
        for file in recovered_files:
            print(f"Recovered: {file}")
    else:
        print("No files recovered.")

if __name__ == '__main__':
    main()
