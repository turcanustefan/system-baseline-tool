import argparse
import os
import zipfile

import binary_baselining
import boot_logon_baselining
import cron_baselining
import user_baselining
import service_baselining
import utils

CRON_BASELINE_FILE = "cron_baseline"
BOOT_LOGON_BASELINE_FILE = "boot_logon_baseline"
BINARY_BASELINE_FILE = "binary_baseline"
SERVICE_BASELINE_FILE = "service_baseline"
USER_BASELINE_FILE = "user_baseline"

def zip_folder(folder_path, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_obj:
        for foldername, subfolders, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                zip_obj.write(file_path, os.path.relpath(file_path, folder_path))

def create_baselines(baseline_name):
    baseline_folder = os.path.join(os.getcwd(), baseline_name)
    if not os.path.exists(baseline_folder):
        # Create the directory
        os.mkdir(baseline_folder)
    binary_baselining.create_baseline(os.path.join(baseline_folder, BINARY_BASELINE_FILE))
    boot_logon_baselining.create_baseline(os.path.join(baseline_folder, BOOT_LOGON_BASELINE_FILE))
    cron_baselining.create_baseline(os.path.join(baseline_folder, CRON_BASELINE_FILE))
    user_baselining.create_baseline(os.path.join(baseline_folder, USER_BASELINE_FILE))
    service_baselining.create_baseline(os.path.join(baseline_folder, SERVICE_BASELINE_FILE))
    zip_folder(baseline_folder, baseline_name + ".zip")


def compare_baselines(old_baseline, new_baseline):

    with zipfile.ZipFile(old_baseline, 'r') as zip_file:
        zip_file.extractall(old_baseline.split('.')[0])
    with zipfile.ZipFile(new_baseline, 'r') as zip_file:
        zip_file.extractall(new_baseline.split('.')[0])

    reports_folder = os.path.join(os.getcwd(), 'reports')
    if not os.path.exists(reports_folder):
        # Create the directory
        os.mkdir(reports_folder)

    # BINARY BASELINE
    baseline1_file = os.path.join(old_baseline.split('.')[0], BINARY_BASELINE_FILE)
    baseline2_file = os.path.join(new_baseline.split('.')[0], BINARY_BASELINE_FILE)
    binary_report = os.path.join(reports_folder, BINARY_BASELINE_FILE + ".html")
    binary_baselining.compare_baselines(baseline1_file, baseline2_file, binary_report)
    
    baseline1_file = os.path.join(old_baseline.split('.')[0], BOOT_LOGON_BASELINE_FILE)
    baseline2_file = os.path.join(new_baseline.split('.')[0], BOOT_LOGON_BASELINE_FILE)
    boot_logon_report = os.path.join(reports_folder, BOOT_LOGON_BASELINE_FILE + ".html")
    utils.compare_baselines_content(baseline1_file, baseline2_file, boot_logon_report)

    baseline1_file = os.path.join(old_baseline.split('.')[0], CRON_BASELINE_FILE)
    baseline2_file = os.path.join(new_baseline.split('.')[0], CRON_BASELINE_FILE)
    cron_report = os.path.join(reports_folder, CRON_BASELINE_FILE + ".html")
    utils.compare_baselines_content(baseline1_file, baseline2_file, cron_report)

    baseline1_file = os.path.join(old_baseline.split('.')[0], USER_BASELINE_FILE)
    baseline2_file = os.path.join(new_baseline.split('.')[0], USER_BASELINE_FILE)
    user_report = os.path.join(reports_folder, USER_BASELINE_FILE + ".html")
    utils.compare_baselines_content(baseline1_file, baseline2_file, user_report)

    baseline1_file = os.path.join(old_baseline.split('.')[0], SERVICE_BASELINE_FILE)
    baseline2_file = os.path.join(new_baseline.split('.')[0], SERVICE_BASELINE_FILE)
    service_report = os.path.join(reports_folder, SERVICE_BASELINE_FILE + ".html")
    utils.compare_baselines_content(baseline1_file, baseline2_file, service_report)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate or compare baselines for system files')
    subparsers = parser.add_subparsers(dest='command', help='commands')

    # create subparser
    create_parser = subparsers.add_parser('create', help='Create baseline')
    create_parser.add_argument('baseline_name', type=str, help='Name of the baseline you want to create')

    # compare subparser
    compare_parser = subparsers.add_parser('compare', help='compare two baselines')
    compare_parser.add_argument('old_baseline_file', type=str, help='baseline file for the old system state')
    compare_parser.add_argument('new_baseline_file', type=str, help='baseline file for the new system state')
    #compare_parser.add_argument('report_file', type=str, help='output file to write comparison report to')

    args = parser.parse_args()

    if args.command == 'create':
        create_baselines(args.baseline_name)
    elif args.command == 'compare':
        compare_baselines(args.old_baseline_file, args.new_baseline_file)
