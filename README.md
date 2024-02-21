# Autocopy

This script automates the process of copying files from the instrument to a designated folder on the NAS once they are completed.

## Prerequisites:

Ensure that Python is installed on the machine.

## Configuration:

The script's behavior can be customized via the config.json file, which contains the following adjustable settings:
* `user_folders`: A dictionary where each ETH-ID corresponds to the path of the target folder on the NAS. Only files from users listed in user_folders will be copied.
* `minimum_size_mb`: Specifies the minimum file size (in megabytes) for a file to be copied, thus avoiding copying empty or incomplete files.
* `source_folder`: The network drive path of the instrument where the files are generated.
nas_folder: The network drive name of the NAS where the files will be copied. This might vary depending on the machine.
* `wait_time_size_change_sec`: The duration to wait before checking if the file size has changed within a certain time period (in seconds).
    
