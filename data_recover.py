import os
import json
import sys
from subprocess import run

# This part remains mostly the same as the logic you already have
class DataRecoveryTool:
    def __init__(self):
        print("Initializing DataRecoveryTool...")
        self.file_signatures = self.load_file_signatures()
        self.selected_signatures = {}

    def load_file_signatures(self):
        """Load file signatures from the JSON file."""
        print("Loading file signatures...")
        try:
            with open("sign.json", "r") as file:
                print("Opened 'sign.json'.")
                signatures = json.load(file)
                print("Parsed JSON:", signatures)
                for file_type in signatures:
                    if "header" in signatures[file_type]:
                        signatures[file_type]["header"] = bytes.fromhex(signatures[file_type]["header"])
                    if "footer" in signatures[file_type] and signatures[file_type]["footer"] is not None:
                        signatures[file_type]["footer"] = bytes.fromhex(signatures[file_type]["footer"])
                print("File signatures processed.")
                return signatures
        except FileNotFoundError:
            print("Error: File 'sign.json' not found.")
            sys.exit()
        except json.JSONDecodeError:
            print("Error: Invalid JSON format.")
            sys.exit()
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            sys.exit()


    def recover_files(self, source_folder, destination_folder):
        try:
            if not source_folder or not destination_folder:
                print("Source or destination folder not selected.")
                return

            if not self.selected_signatures:
                print("No file types selected for recovery.")
                return

            for root, _, files in os.walk(source_folder):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    self.check_and_recover_file(file_path, destination_folder)
        except Exception as e:
            print(f"Error during recovery: {str(e)}")

    def check_and_recover_file(self, file_path, destination_folder):
        try:
            with open(file_path, "rb") as file:
                content = file.read()
                for file_type, signature in self.selected_signatures.items():
                    if content.startswith(signature["header"]) and (
                        "footer" not in signature
                        or signature["footer"] is None
                        or content.endswith(signature["footer"])
                    ):
                        self.save_recovered_file(file, file_type, destination_folder)
                        break
        except Exception as e:
            print(f"Failed to process file {file_path}: {str(e)}")

    def save_recovered_file(self, file, file_name, destination_folder):
        try:
            destination_path = os.path.join(destination_folder, os.path.basename(file_name))
            with open(destination_path, "wb") as dest_file:
                dest_file.write(file.read())
            print(f"Recovered: {destination_path}")
        except Exception as e:
            print(f"Failed to save file: {str(e)}")

if __name__ == "__main__":
    tool = DataRecoveryTool()
