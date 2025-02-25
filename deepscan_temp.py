#!/usr/bin/python3

import pytsk3
import pyewf
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("deep_scan.log"), logging.StreamHandler()],
)


class DiskImageHandler:
    """Handles disk image operations."""

    def __init__(self, image_path):
        self.image_path = image_path
        self.ewf_handle = None

    def open_image(self):
        """Open the disk image using pyewf."""
        try:
            self.ewf_handle = pyewf.handle()
            self.ewf_handle.open(self.image_path)
            logging.info(f"Successfully opened disk image: {self.image_path}")
        except Exception as e:
            logging.error(f"Failed to open disk image: {e}")
            raise

    def close_image(self):
        """Close the disk image."""
        if self.ewf_handle:
            self.ewf_handle.close()
            logging.info("Closed disk image.")


class FileRecoverer:
    """Handles file recovery operations."""

    def __init__(self, image_handler):
        self.image_handler = image_handler
        self.img_info = pytsk3.Img_Info(image_handler.ewf_handle)
        self.filesystem = pytsk3.FS_Info(self.img_info)

    def extract_file(self, file_entry, output_path):
        """Extract a file from the disk image."""
        try:
            with open(output_path, "wb") as f:
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
            logging.info(f"Recovered file: {output_path}")
            return output_path
        except Exception as e:
            logging.error(f"Failed to recover file {output_path}: {e}")
            return None

    def traverse_directory(self, directory, output_dir, deep_scan=False):
        """Traverse a directory and recover files."""
        recovered_files = []
        for entry in directory:
            if entry.info.name.name in [b".", b".."]:
                continue
            try:
                f_type = entry.info.meta.type
                if f_type == pytsk3.TSK_FS_META_TYPE_DIR:
                    sub_directory = entry.as_directory()
                    recovered_files.extend(
                        self.traverse_directory(sub_directory, output_dir, deep_scan)
                    )
                elif f_type == pytsk3.TSK_FS_META_TYPE_REG:
                    if deep_scan or entry.info.meta.flags & pytsk3.TSK_FS_META_FLAG_UNALLOC:
                        file_name = entry.info.name.name.decode(errors="ignore")
                        output_path = os.path.join(output_dir, file_name)
                        recovered_file = self.extract_file(entry, output_path)
                        if recovered_file:
                            recovered_files.append(recovered_file)
            except AttributeError as e:
                logging.warning(f"Skipping entry due to error: {e}")
        return recovered_files

    def recover_files(self, output_dir, deep_scan=False):
        """Recover files from the disk image."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logging.info(f"Created output directory: {output_dir}")

        root_directory = self.filesystem.open_dir("/")
        return self.traverse_directory(root_directory, output_dir, deep_scan)

    def recover_file(self, file_path, output_path):
        """Recover a specific file from the disk image."""
        try:
            file_entry = self.filesystem.open(file_path)
            return self.extract_file(file_entry, output_path)
        except Exception as e:
            logging.error(f"Failed to recover file {file_path}: {e}")
            return None


def get_user_input(prompt, default=None):
    """Get input from the user with an optional default value."""
    user_input = input(prompt).strip()
    return user_input if user_input else default


def main():
    print("Welcome to Deep Scan - A Forensic File Recovery Tool\n")

    # Ask for the disk image path
    image_path = get_user_input("Enter the path to the disk image (e.g., /path/to/image.E01): ")
    if not os.path.exists(image_path):
        print(f"Error: The file '{image_path}' does not exist.")
        return

    # Ask for the output directory
    output_dir = get_user_input(
        "Enter the output directory to save recovered files (e.g., /path/to/output): ",
        default="recovered_files",
    )

    # Ask if the user wants to perform a deep scan
    deep_scan = (
        get_user_input("Perform a deep scan to recover deleted files? (y/n): ").lower() == "y"
    )

    # Ask if the user wants to recover a specific file or all files
    recover_option = get_user_input(
        "Do you want to recover a specific file or all files? (file/all): "
    ).lower()

    try:
        image_handler = DiskImageHandler(image_path)
        image_handler.open_image()
        recoverer = FileRecoverer(image_handler)

        if recover_option == "file":
            file_path = get_user_input("Enter the path of the file to recover (e.g., /path/to/file.txt): ")
            output_path = os.path.join(output_dir, os.path.basename(file_path))
            recovered_file = recoverer.recover_file(file_path, output_path)
            if recovered_file:
                print(f"\nRecovered file: {recovered_file}")
            else:
                print("\nFile not recovered.")

        elif recover_option == "all":
            recovered_files = recoverer.recover_files(output_dir, deep_scan)
            if recovered_files:
                print("\nRecovered files:")
                for file in recovered_files:
                    print(f"- {file}")
            else:
                print("\nNo files recovered.")

        else:
            print("Invalid option. Please choose 'file' or 'all'.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        image_handler.close_image()


if __name__ == "__main__":
    main()
    