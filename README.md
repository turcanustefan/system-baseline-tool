# System Baseline Tool
The System Baseline Tool is a command-line tool for generating and comparing baselines for various system files. It can generate baselines for the following categories of files:

- Binary files
- Boot and logon scripts
- Cron jobs
- User directories and files
- System services

The tool can also compare two baselines to generate reports on changes between the two system states.

# Usage
The tool can be run with the following commands:

## Create Baseline
Use the following command to create a baseline:
`python main.py create <baseline_name>`
The <baseline_name> argument specifies the name of the baseline you want to create. This will generate a folder containing baseline files for each category, as well as a ZIP file of the folder.

## Compare Baselines
Use the following command to compare two baselines:
`python main.py compare <old_baseline_file> <new_baseline_file>`
The <old_baseline_file> and <new_baseline_file> arguments specify the paths to the baseline files for the old and new system states, respectively. This will generate a report for each category in the reports folder.

# Files
The following files are included in this repository:

- binary_baselining.py: Contains functions to create and compare baselines for binary files.
- boot_logon_baselining.py: Contains functions to create and compare baselines for boot and login configurations.
- cron_baselining.py: Contains functions to create and compare baselines for cron jobs.
- service_baselining.py: Contains functions to create and compare baselines for system services.
- user_baselining.py: Contains functions to create and compare baselines for user configurations.
- utils.py: Contains utility functions used by other modules.
- baseline.py: The main script that invokes the other modules.

# License
This project is licensed under the MIT License (https://opensource.org/license/mit/).