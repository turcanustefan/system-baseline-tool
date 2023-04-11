import os
import base64
import hashlib

BASELINE_FILE = "cron_baseline"

CRON_DIRS = [
    '/var/spool/cron/', 
    '/etc/cron.d/', 
    '/etc/cron.hourly/', 
    '/etc/cron.daily/', 
    '/etc/cron.weekly/', 
    '/etc/cron.monthly/',
    ]
CRON_FILE = '/etc/crontab'

def get_cron_jobs():
    """Returns a list of paths to all cron jobs"""
    cron_jobs = []
    for cron_dir in CRON_DIRS:
        if os.path.isdir(cron_dir):
            for root, dirs, files in os.walk(cron_dir):
                for file in files:
                    cron_jobs.append(os.path.join(root, file))
    cron_jobs.append(CRON_FILE)
    return cron_jobs


def create_baseline(baseline_file):
    """Creates a baseline of all cron jobs"""
    baseline = {}
    cron_jobs = get_cron_jobs()
    for job_path in cron_jobs:
        with open(job_path, 'rb') as f:
            content = f.read()
            content_b64 = base64.b64encode(content).decode('utf-8')
            hash_value = hashlib.sha256(content).hexdigest()
        baseline[job_path] = {
            'hash': hash_value,
            'content': content_b64
        }
    with open(baseline_file, 'w') as f:
        for job_path, job_data in baseline.items():
            f.write(f"{job_path} {job_data['hash']} {job_data['content']}\n")
    print(f"Baseline created at {baseline_file}")