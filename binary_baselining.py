"""
Script developed by https://github.com/turcanustefan/system-baseline-tool
This script is licensed under the MIT License.
You are free to use, modify, and distribute this software as long as
you include the original copyright notice and license terms.
This software is provided "as is", without warranty of any kind.
"""
import os
import difflib
from concurrent.futures import ThreadPoolExecutor
from utils import hash_file, hash_file_md5, generate_report, is_hash_in_hashdb2


def compare_baselines(baseline1, baseline2, report, md5sums, use_md5sums=False):
    """Compare two baselines and write differences to an HTML report file."""
    
    old_baseline = {}
    with open(baseline1, 'r') as f:
        for line in f:
            try:
                file_path, file_hash = line.strip().split(' ')
                old_baseline[file_path] = file_hash
            except:
                continue

    new_baseline = {}
    with open(baseline2, 'r') as f:
        for line in f:
            try:
                file_path, file_hash = line.strip().split(' ')
                new_baseline[file_path] = file_hash
            except:
                continue

    added_files = {}
    removed_files = {}
    changed_files = {}

    baseline1_lines = []
    baseline2_lines = []

    for file_path, new_file_hash in new_baseline.items():
        old_file_hash = old_baseline.get(file_path)
        if not old_file_hash:
            found_hash = None
            if use_md5sums:
                found_hash = is_hash_in_hashdb2(md5sums, file_path, new_file_hash)
            if not found_hash:
                added_files[file_path] = (None, new_file_hash)
                baseline1_lines.append(f"{file_path} X")
                baseline2_lines.append(f"{file_path} {new_file_hash}")
        elif old_file_hash != new_file_hash:
            found_hash = None
            if use_md5sums:
                found_hash = is_hash_in_hashdb2(md5sums, file_path, new_file_hash)
            if not found_hash:
                changed_files[file_path] = (new_file_hash, new_file_hash)
                baseline2_lines.append(f"{file_path} {new_file_hash}")
                baseline1_lines.append(f"{file_path} {old_file_hash}")
    report_data = []
    for i in range(0, len(baseline1_lines), 100):
        results = difflib.HtmlDiff(tabsize=2).make_file(baseline1_lines[i:i+100], baseline2_lines[i:i+100], baseline1, baseline2)
        report_data.append(results)
    #results = generate_report(added_files, removed_files, changed_files)

    report_html = '<html><body>' + ''.join(report_data) + '</body></html>'
    with open(report, "w") as f:
        f.write(report_html)


def get_binaries():
    """Get a list of all binaries in PATH directories."""
    binaries = []
    paths = os.environ["PATH"].split(os.pathsep)
    for path in paths:
        if os.path.isdir(path):
            for filename in os.listdir(path):
                filepath = os.path.join(path, filename)
                if os.path.isfile(filepath) and os.access(filepath, os.X_OK):
                    binaries.append(filepath)
    return binaries


def get_libraries():
    """Get a list of all shared libraries on the system."""
    libraries = []
    known_lib_dirs = ["/usr/lib", "/usr/local/lib", "/usr/local/lib64", "/usr/lib64"]
    for lib_dir in known_lib_dirs:
        for root, dirs, files in os.walk(lib_dir):
            for filename in files:
                if filename.endswith(".so"):
                    libraries.append(os.path.join(root, filename))
    return libraries


def get_kernel_binaries():
    """Get a list of all shared libraries on the system."""
    kernel_binaries = []
    kernel_module_dir = '/lib/modules/{}/kernel/'.format(os.uname().release)
    for root, dirs, files in os.walk(kernel_module_dir):
        for filename in files:
            path = os.path.join(root, filename)
            # We ignore symbolic links as they can cause permission issues and also because
            # their contents can change without the file itself changing.
            if os.path.islink(path):
                path = os.path.realpath(path)
            if filename.endswith(".ko"):
                kernel_binaries.append(path)
    return kernel_binaries


def get_systemd_generators():
    """Get a list of all systemd generators on the system."""
    systemd_generators = []
    systemd_generators_dirs = [
        '/etc/systemd/system-generators/',
        '/usr/local/lib/systemd/system-generators/',
        '/lib/systemd/system-generators/'
    ]
    for lib_dir in systemd_generators_dirs:
        for root, dirs, files in os.walk(lib_dir):
            for filename in files:
                path = os.path.join(root, filename)
                if os.path.islink(path):
                    path = os.path.realpath(path)
                systemd_generators.append(path)

    return systemd_generators


def hash_files(filepaths, num_threads=4):
    """Hash a list of files using multiple threads."""
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        results = list(executor.map(hash_file_md5, filepaths)) # hash_files
    return dict(zip(filepaths, results))


def create_baseline(baseline_file):
    """Create a baseline of all binaries and libraries on the system."""
    binaries = get_binaries()
    libraries = get_libraries()
    kernel_binaries = get_kernel_binaries()
    systemd_generators = get_systemd_generators()
    filepaths = binaries + libraries + kernel_binaries + systemd_generators
    hashes = hash_files(filepaths)
    with open(baseline_file, "w") as f:
        for filepath, hashvalue in hashes.items():
            f.write(f"{filepath} {hashvalue}\n")
    print(f"Baseline created at {baseline_file}")