"""
Script developed by https://github.com/turcanustefan/system-baseline-tool
This script is licensed under the MIT License.
You are free to use, modify, and distribute this software as long as
you include the original copyright notice and license terms.
This software is provided "as is", without warranty of any kind.
"""
import hashlib
import os
from datetime import datetime
import base64
import difflib
import importlib.util
import magic

def is_plain_text(file_path):
    try:
        file_type = magic.from_file(file_path, mime=True)
        if file_type == 'inode/symlink': # if symlink, find the real path
            real_path = os.path.realpath(file_path)
            file_type = magic.from_file(real_path, mime=True)
        return file_type.startswith('text/')
    except Exception as e:
        print(f"Error determining file type: {e}")
        return False
    

def is_binary(file_path):
    """Checks if the file is binary based on the first few bytes."""
    # List of common binary file signatures
    binary_signatures = [
        b'\x7fELF',     # ELF binary
        b'\x4d\x5a',    # DOS MZ executable
        b'\xca\xfe\xba\xbe' # Java class file
        # Add more signatures as needed
    ]
    with open(file_path, 'rb') as f:
        start_bytes = f.read(4)
        for signature in binary_signatures:
            if start_bytes.startswith(signature):
                return True
    return False


def module_exists(module_name):
    """Check if a module can be imported without actually importing it."""
    module_spec = importlib.util.find_spec(module_name)
    return module_spec is not None


def hash_file(file_path):
    """
    Generate the SHA256 hash of a file.

    Args:
        file_path (str): Path to the file

    Returns:
        str: The SHA256 hash of the file
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def hash_file_md5(file_path):
    """
    Generate the MD5 hash of a file.

    Args:
        file_path (str): Path to the file

    Returns:
        str: The MD5 hash of the file
    """
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            md5_hash.update(byte_block)
    return md5_hash.hexdigest()

def create_dir(directory):
    """
    Create a directory if it doesn't already exist.

    Args:
        directory (str): Path to the directory
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def generate_timestamp():
    """
    Generate a timestamp string.

    Returns:
        str: The timestamp string
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d_%H-%M-%S")


def is_hash_in_hashdb(hashdb_file, target_hash):
    with open(hashdb_file, 'r') as f:
        for line in f:
            if not line.startswith('#'):
                hash_value, file_path = line.split()
                if hash_value == target_hash:
                    return True, file_path.strip()
    return False, None


def is_hash_in_hashdb2(md5sums, file_path, target_hash):
    for package in md5sums:
        for file in md5sums[package]:
            # print(target_hash, md5sums[package][file])
            if target_hash == md5sums[package][file]:
                print(f"{file_path} is in the hashdb {package} {file} {target_hash}")
                return True
    return False    


def compare_baselines_content(old_baseline_file, new_baseline_file, report):
    """Compares two baseline files to identify added, removed, and changed files."""
    old_baseline = {}
    with open(old_baseline_file, 'r') as f:
        for line in f:
            try:
                file_path, file_hash, file_content_b64 = line.strip().split(' ')
                if file_path.endswith('bdx'):
                    print(file_path, file_hash, file_content)
                if file_content_b64:
                    file_content = base64.b64decode(file_content_b64.encode()).decode()
                else:
                    file_content = None
                old_baseline[file_path] = {'hash': file_hash, 'content': file_content}
            except:
                continue

    new_baseline = {}
    with open(new_baseline_file, 'r') as f:
        for line in f:
            try:
                file_path, file_hash, file_content_b64 = line.strip().split(' ')
                if file_content_b64:
                    file_content = base64.b64decode(file_content_b64.encode()).decode()
                else:
                    file_content = None
                new_baseline[file_path] = {'hash': file_hash, 'content': file_content}
            except:
                continue

    added_files = {}
    removed_files = {}
    changed_files = {}

    # Identify added and changed files
    for file_path, new_file_data in new_baseline.items():
        old_file_data = old_baseline.get(file_path)
        if not old_file_data:
            if new_file_data['content']:
                added_files[file_path] = (None, new_file_data['content'])
            else:
                added_files[file_path] = (None, new_file_data['hash'])
        elif old_file_data['hash'] != new_file_data['hash']:
            if new_file_data['content']:
                changed_files[file_path] = (old_file_data['content'], new_file_data['content'])
            else:
                changed_files[file_path] = (old_file_data['hash'], new_file_data['hash'])

    # Identify removed files
    for file_path, old_file_data in old_baseline.items():
        new_file_data = new_baseline.get(file_path)
        if not new_file_data:
            if old_file_data['content']:
                removed_files[file_path] = (old_file_data['content'], None)
            else:
                removed_files[file_path] = (old_file_data['hash'], None)

    results = generate_report(added_files, removed_files, changed_files)

    with open(report, "w") as f:
        f.write(results)


def generate_report(added_files, removed_files, changed_files):
    """Generates an HTML report of added, removed, and changed files."""
    report = []
    
    if added_files:
        report.append('<h2>Added files:</h2>')
        for path, (content1, content2) in added_files.items():
            report.append(f'<h3>{path}</h3>')
            diff = difflib.HtmlDiff().make_file("", content2.splitlines())
            report.extend(diff.split('\n')[3:-1])
    
    if removed_files:
        report.append('<h2>Removed files:</h2>')
        for path, (content1, content2) in removed_files.items():
            report.append(f'<h3>{path}</h3>')
            diff = difflib.HtmlDiff().make_file(content1.splitlines(), "")
            report.extend(diff.split('\n')[3:-1])
    
    if changed_files:
        report.append('<h2>Changed files:</h2>')
        for path, (content1, content2) in changed_files.items():
            report.append(f'<h3>{path}</h3>')
            diff = difflib.HtmlDiff().make_file(content1.splitlines(), content2.splitlines())
            report.extend(diff.split('\n')[3:-1])
    
    report_html = '<html><body>' + ''.join(report) + '</body></html>'
    return report_html