import hashlib
import base64
import os


COMMON_LOGON_DIRS = [
    '/etc/rc.d/', 
    '/etc/rc.local/', 
    '/etc/init.d/',
    '/etc/update-motd.d/'
    ]

def create_baseline(baseline_file):
    """Generates a baseline of all files in a directory."""
    baseline = {}
    for directory in COMMON_LOGON_DIRS:
        for root, dirs, files in os.walk(directory):
            for filename in files:
                path = os.path.join(root, filename)
                with open(path, 'rb') as f:
                    content = f.read()
                    content_b64 = base64.b64encode(content).decode()
                    hash_value = hashlib.sha256(content).hexdigest()
                    baseline[path] = {
                        'hash': hash_value, 
                        'content': content_b64
                    }

    with open(baseline_file, 'w') as f:
        for file_path, file_data in baseline.items():
            f.write(f"{file_path} {file_data['hash']} {file_data['content']}\n")
    print(f"Baseline created at {baseline_file}")

    return baseline