import os
import hashlib
import base64


SERVICE_DIRS = [
    '/etc/systemd/system/', 
    '/lib/systemd/system/',
    '/lib/systemd/user/',
    '/etc/systemd/user/'
]

def create_baseline(baseline_file):
    """Generates a baseline of services on the host."""
    baseline = {}

    # Baseline common SERVICE_DIRS directories
    for directory in SERVICE_DIRS:
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if filename.endswith('.service'):
                    path = os.path.join(root, filename)
                    with open(path, 'rb') as f:
                        content = f.read()
                        content_b64 = base64.b64encode(content).decode()
                        hash_value = hashlib.sha256(content).hexdigest()
                        baseline[path] = {
                            'hash': hash_value, 
                            'content': content_b64
                        }
    # Write baseline to file
    with open(baseline_file, 'w') as f:
        for file_path, file_data in baseline.items():
            f.write(f"{file_path} {file_data['hash']} {file_data['content']}\n")