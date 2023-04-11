import os
import hashlib
import base64
import pwd


# list of common directories
COMMON_USER_DIRS = [
    '/etc/sudoers.d/',
    '/etc/pam.d/',
    '/etc/profile.d/'
]

# list of common user files and configs to baseline
COMMON_USER_FILES = [
    '/etc/passwd',
    '/etc/group',
    '/etc/sudoers',
    '/etc/shadow',
    '/etc/login.defs',
    '/etc/security/limits.conf',
    '/etc/pam.conf',
    '/etc/pam.d/common-auth',
    '/etc/pam.d/common-password',
    '/etc/pam.d/common-session',
    '/etc/pam.d/common-account',
    '/etc/ssh/sshd_config',
    '/etc/profile'
]

# list of per-user files and configs to baseline
USER_FILES = [
    '.bashrc',
    '.bash_profile',
    '.bash_logout',
    '.profile',
    '.ssh/authorized_keys',
]

def create_baseline(baseline_file):
    """Generates a baseline of user files and configs for specified users."""
    baseline = {}

    # Baseline common user directories
    for directory in COMMON_USER_DIRS:
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

    # Baseline common user files and configs
    for file_path in COMMON_USER_FILES:
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                content = f.read()
                content_b64 = base64.b64encode(content).decode()
                hash_value = hashlib.sha256(content).hexdigest()
                baseline[file_path] = {
                    'hash': hash_value,
                    'content': content_b64
                }

    # Baseline per-user files and configs
    users = pwd.getpwall()
    for user in users:
        user_home_dir = user.pw_dir
        if os.path.isdir(user_home_dir):
            for file_path in USER_FILES:
                full_file_path = os.path.join(user_home_dir, file_path)
                if os.path.isfile(full_file_path):
                    with open(full_file_path, 'rb') as f:
                        content = f.read()
                        content_b64 = base64.b64encode(content).decode()
                        hash_value = hashlib.sha256(content).hexdigest()
                        baseline[full_file_path] = {
                            'hash': hash_value,
                            'content': content_b64
                        }

    # Write baseline to file
    with open(baseline_file, 'w') as f:
        for file_path, file_data in baseline.items():
            f.write(f"{file_path} {file_data['hash']} {file_data['content']}\n")

