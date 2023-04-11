import hashlib
import os
from datetime import datetime
import base64
import difflib
import tarfile


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


def compare_baselines_content(old_baseline_file, new_baseline_file, report):
    """Compares two baseline files to identify added, removed, and changed files."""
    old_baseline = {}
    with open(old_baseline_file, 'r') as f:
        for line in f:
            try:
                file_path, file_hash, file_content_b64 = line.strip().split(' ')
                file_content = base64.b64decode(file_content_b64.encode()).decode()
                old_baseline[file_path] = {'hash': file_hash, 'content': file_content}
            except:
                continue

    new_baseline = {}
    with open(new_baseline_file, 'r') as f:
        for line in f:
            try:
                file_path, file_hash, file_content_b64 = line.strip().split(' ')
                file_content = base64.b64decode(file_content_b64.encode()).decode()
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
            added_files[file_path] = (None, new_file_data['content'])
        elif old_file_data['hash'] != new_file_data['hash']:
            changed_files[file_path] = (old_file_data['content'], new_file_data['content'])

    # Identify removed files
    for file_path, old_file_data in old_baseline.items():
        new_file_data = new_baseline.get(file_path)
        if not new_file_data:
            removed_files[file_path] = (old_file_data['content'], None)

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