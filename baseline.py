"""
Script developed by https://github.com/turcanustefan/system-baseline-tool
This script is licensed under the MIT License.
You are free to use, modify, and distribute this software as long as
you include the original copyright notice and license terms.
This software is provided "as is", without warranty of any kind.
"""
import argparse
import os
import zipfile

import binary_baselining 
import boot_logon_baselining
import cron_baselining
import user_baselining
import service_baselining
import custom_baselining
import utils
import hashdb
# try:
#     import create_hashdb
# except ImportError:
#     # Handle the case where the module doesn't exist
#     print("Module 'create_hashdb' failed to load.")


CRON_BASELINE_FILE = "cron_baseline"
BOOT_LOGON_BASELINE_FILE = "boot_logon_baseline"
BINARY_BASELINE_FILE = "binary_baseline"
SERVICE_BASELINE_FILE = "service_baseline"
USER_BASELINE_FILE = "user_baseline"
CUSTOM_BASELINE_FILE = "custom_baseline"
HASHDB_FILE = 'hashdb'

def zip_folder(folder_path, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_obj:
        for foldername, subfolders, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                zip_obj.write(file_path, os.path.relpath(file_path, folder_path))


def create_baselines(baseline_name):
    config_file = 'config.json'
    baseline_folder = os.path.join(os.getcwd(), baseline_name)
    if not os.path.exists(baseline_folder):
        # Create the directory
        os.mkdir(baseline_folder)
    
    # HASHDB
    md5sums_dir = '/var/lib/dpkg/info'
    if os.path.isdir(md5sums_dir):
        output_file = os.path.join(baseline_folder, HASHDB_FILE)
        md5sums = hashdb.extract_md5sums(md5sums_dir)
        hashdb.save_to_file(md5sums, output_file)
        print(f"MD5 sums saved to {output_file}")
    # BINARY
    binary_baselining.create_baseline(os.path.join(baseline_folder, BINARY_BASELINE_FILE))
    # BOOT
    boot_logon_baselining.create_baseline(os.path.join(baseline_folder, BOOT_LOGON_BASELINE_FILE))
    # CRON
    cron_baselining.create_baseline(os.path.join(baseline_folder, CRON_BASELINE_FILE))
    # USER
    user_baselining.create_baseline(os.path.join(baseline_folder, USER_BASELINE_FILE))
    # SERVICE
    service_baselining.create_baseline(os.path.join(baseline_folder, SERVICE_BASELINE_FILE))
    # CUSTOM
    custom_baselining.create_baseline(config_file, os.path.join(baseline_folder, CUSTOM_BASELINE_FILE))
    zip_folder(baseline_folder, baseline_name + ".zip")


def compare_baselines(old_baseline, new_baseline, use_hash_db=False):
    old_filename, old_file_extension = os.path.splitext(old_baseline)
    new_filename, new_file_extension = os.path.splitext(new_baseline)
    
    with zipfile.ZipFile(old_baseline, 'r') as zip_file:
        zip_file.extractall(old_filename)
    with zipfile.ZipFile(new_baseline, 'r') as zip_file:
        zip_file.extractall(new_filename)

    reports_folder = os.path.join(os.getcwd(), 'reports','{0}'.format(new_filename.split('\\')[-1]))
    if not os.path.exists(reports_folder):
        # Create the directory
        os.makedirs(reports_folder)

    # Instantiate HASHDB
    md5sums = hashdb.read_hashdb(os.path.join(new_filename, HASHDB_FILE))

    # BINARY BASELINE
    baseline1_file = os.path.join(old_filename, BINARY_BASELINE_FILE)
    baseline2_file = os.path.join(new_filename, BINARY_BASELINE_FILE)
    binary_report = os.path.join(reports_folder, BINARY_BASELINE_FILE + ".html")
    binary_baselining.compare_baselines(baseline1_file, baseline2_file, binary_report, md5sums, use_hash_db)
    # BOOT
    baseline1_file = os.path.join(old_filename, BOOT_LOGON_BASELINE_FILE)
    baseline2_file = os.path.join(new_filename, BOOT_LOGON_BASELINE_FILE)
    boot_logon_report = os.path.join(reports_folder, BOOT_LOGON_BASELINE_FILE + ".html")
    utils.compare_baselines_content(baseline1_file, baseline2_file, boot_logon_report)
    # CRON
    baseline1_file = os.path.join(old_filename, CRON_BASELINE_FILE)
    baseline2_file = os.path.join(new_filename, CRON_BASELINE_FILE)
    cron_report = os.path.join(reports_folder, CRON_BASELINE_FILE + ".html")
    utils.compare_baselines_content(baseline1_file, baseline2_file, cron_report)
    # USER
    baseline1_file = os.path.join(old_filename, USER_BASELINE_FILE)
    baseline2_file = os.path.join(new_filename, USER_BASELINE_FILE)
    user_report = os.path.join(reports_folder, USER_BASELINE_FILE + ".html")
    utils.compare_baselines_content(baseline1_file, baseline2_file, user_report)
    # SERVICE
    baseline1_file = os.path.join(old_filename, SERVICE_BASELINE_FILE)
    baseline2_file = os.path.join(new_filename, SERVICE_BASELINE_FILE)
    service_report = os.path.join(reports_folder, SERVICE_BASELINE_FILE + ".html")
    utils.compare_baselines_content(baseline1_file, baseline2_file, service_report)
    # CUSTOM
    baseline1_file = os.path.join(old_filename, CUSTOM_BASELINE_FILE)
    baseline2_file = os.path.join(new_filename, CUSTOM_BASELINE_FILE)
    service_report = os.path.join(reports_folder, CUSTOM_BASELINE_FILE + ".html")
    utils.compare_baselines_content(baseline1_file, baseline2_file, service_report)


if __name__ == '__main__':
    modules_to_check = ['magic']
    modules_missing = []
    for module in modules_to_check:
        if not utils.module_exists(module):
            print(f"Module '{module}' is not installed.")
            modules_missing.append(module)
            # exit()

    parser = argparse.ArgumentParser(description='Generate or compare baselines for system files')
    subparsers = parser.add_subparsers(dest='command', help='commands')

    # create subparser
    create_parser = subparsers.add_parser('create', help='Create baseline')
    create_parser.add_argument('baseline_name', type=str, help='Name of the baseline you want to create')

    # compare subparser
    compare_parser = subparsers.add_parser('compare', help='compare two baselines')
    compare_parser.add_argument('old_baseline_file', type=str, help='baseline file for the old system state')
    compare_parser.add_argument('new_baseline_file', type=str, help='baseline file for the new system state')
    compare_parser.add_argument('--use-hashdb', action='store_true', default=False, help='Use the hashdb from the baseline to exclude FPs (Debian only).')
    #compare_parser.add_argument('report_file', type=str, help='output file to write comparison report to')

    args = parser.parse_args()

    if args.command == 'create':
        create_baselines(args.baseline_name)
    elif args.command == 'compare':
        compare_baselines(args.old_baseline_file, args.new_baseline_file, args.use_hashdb)
