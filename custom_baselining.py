"""
Script developed by https://github.com/turcanustefan/system-baseline-tool
This script is licensed under the MIT License.
You are free to use, modify, and distribute this software as long as
you include the original copyright notice and license terms.
This software is provided "as is", without warranty of any kind.
"""
import base64
import os
import json
from utils import hash_file, is_binary, is_plain_text
import hashlib

def create_baseline(config_file, baseline_file):
    """Creates a baseline of specified files and folders."""
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Configuration file not found.")
        return

    baseline = {}
    files = config.get('files', [])
    folders = config.get('folders', [])

    if not (files or folders):
        return

    for file_path in files:
        if os.path.isfile(file_path):
            if os.path.islink(file_path):
                file_path = os.path.realpath(file_path)
            if os.path.exists(file_path):
                if is_plain_text(file_path):
                    with open(file_path, 'rb') as f:
                        content = f.read()
                        content_b64 = base64.b64encode(content).decode()
                        hash_value = hashlib.sha256(content).hexdigest()
                        baseline[file_path] = {
                            'hash': hash_value, 
                            'content': content_b64
                        }
                else:
                    baseline[file_path] = hash_file(file_path)
            else:
                print(f"File {file_path} does not exist.")
        else:
            print(f"Path {file_path} is not a file.")

    for folder in folders:
        if os.path.isdir(folder):
            for root, _, files in os.walk(folder):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    if os.path.islink(file_path):
                        file_path = os.path.realpath(file_path)
                    if os.path.exists(file_path):
                        if is_plain_text(file_path):
                            with open(file_path, 'rb') as f:
                                content = f.read()
                                content_b64 = base64.b64encode(content).decode()
                                hash_value = hashlib.sha256(content).hexdigest()
                                baseline[file_path] = {
                                    'hash': hash_value, 
                                    'content': content_b64
                                }
                        else:
                            baseline[file_path] = hash_file(file_path)
        else:
            print(f"Path {folder} is not a directory.")

    with open(baseline_file, "w") as f:
        for filepath, fileinfo in baseline.items():
            if 'content' in fileinfo:
                f.write(f"{filepath} {fileinfo['hash']} {fileinfo['content']}\n")
            else:
                f.write(f"{filepath} {fileinfo}\n")
    print(f"Baseline created at {baseline_file}")