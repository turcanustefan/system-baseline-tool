import os
import difflib
from concurrent.futures import ThreadPoolExecutor
from utils import hash_file

BASELINE_FILE = "binary_baseline"

def compare_baselines(baseline1, baseline2, report):
    """Compare two baselines and write differences to an HTML report file."""
    
    with open(baseline1, 'r') as f:
        baseline1_lines = f.readlines()
        
    with open(baseline2, 'r') as f:
        baseline2_lines = f.readlines()
        
    diff = difflib.HtmlDiff().make_file(baseline1_lines, baseline2_lines, baseline1, baseline2)
    
    with open(report, "w") as f:
        f.write(diff)

def get_binaries():
    """Get a list of all binaries in PATH directories."""
    binaries = []
    paths = os.environ["PATH"].split(os.pathsep)
    for path in paths:
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
                continue
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
                    continue
                systemd_generators.append(path)

    return systemd_generators

def hash_files(filepaths, num_threads=4):
    """Hash a list of files using multiple threads."""
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        results = list(executor.map(hash_file, filepaths))
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
            f.write(f"{hashvalue} {filepath}\n")