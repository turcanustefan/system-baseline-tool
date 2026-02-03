"""
Script developed by https://github.com/turcanustefan/system-baseline-tool
This script is licensed under the MIT License.
You are free to use, modify, and distribute this software as long as
you include the original copyright notice and license terms.
This software is provided "as is", without warranty of any kind.
"""
import os

def extract_md5sums(md5sums_dir):
    md5sums = {}
    for file_name in os.listdir(md5sums_dir):
        if file_name.endswith('.md5sums'):
            package_name = file_name.split('.')[0]
            md5sums[package_name] = {}
            with open(os.path.join(md5sums_dir, file_name), 'r') as f:
                for line in f:
                    md5, file_path = line.strip().split(maxsplit=1)
                    file_path = f"/{file_path}"
                    md5sums[package_name][file_path] = md5
    return md5sums

def save_to_file(md5sums, output_file):
    with open(output_file, 'w') as f:
        for package, files in md5sums.items():
            for file_path, md5sum in files.items():
                f.write(f"{package} {file_path} {md5sum}\n")

def read_hashdb(hashdb_file):
    hashdb = {}
    with open(hashdb_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            package = parts[0]
            file_path = parts[1]
            md5sum = parts[2]
            if package not in hashdb:
                hashdb[package] = {}
            hashdb[package][file_path] = md5sum
    return hashdb

# def main():
#     md5sums_dir = '/var/lib/dpkg/info'
#     output_file = '/tmp/hashdb'
#     md5sums = extract_md5sums(md5sums_dir)
#     save_to_file(md5sums, output_file)
#     print(f"MD5 sums saved to {output_file}")

# if __name__ == "__main__":
#     main()
