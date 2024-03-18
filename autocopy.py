import datetime
import os
from tqdm import tqdm as tqdm
from shutil import copyfile, copytree
import time
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import numpy as np
import json

with open('config.json') as f:
    config = json.load(f)

wait_time_size_change_sec = config["wait_time_size_change_sec"]
minimum_size_mb =  config["minimum_size_mb"]
target_base = config["target_base"]
source_folder = config["source_folder"]
wait_time_check_files_sec = config["wait_time_check_files_sec"]
user_folders = config["user_folders"]
nas_folder = config["nas_folder"]

def get_full_size_mb(path: str):
    """Get size of path in MB, accepts file.

    Args:
        path (str): Path to check.

    Returns:
        _type_: Size in Mb.
    """
    if os.path.isfile(path):
        return os.path.getsize(path) / (1024**2)
    else:
        print(f"Not file {path}")
        return np.nan
    
def get_target_folder(user_folder:str, experiment_id:str, experiment_type) -> str:
    """
    create folder with experiment if it doesnt exist 
    return name of target folder
    """
    # create folder with experimentid in user folder if it doesnt exist
    experiment_path = os.path.join(user_folder, experiment_id)
    if not os.path.exists(experiment_path):
        os.makedirs(experiment_path)

    # if experiment_type is not None create folder with experimenttype in experimentid folder
    # return spath tring with newly created folder either with user_folder+experiment_id 
    # or user_folder+experiment_id + experiment_type
    if experiment_type:
        experiment_type_path = os.path.join(experiment_path, experiment_type)
        if not os.path.exists(experiment_type_path):
            os.makedirs(experiment_type_path)
        return experiment_type_path
    else:
        return experiment_path
    
def copy_file(file_to_copy:str, user_folder:str, source:str, file_dict:dict):
    # fileformat date_instrumentid_ethid_experimentid_liptc_(batch)..raw
    experiment_id = file_to_copy.split("_")[2]
    experiment_type = file_to_copy.split("_")[3] 
    if experiment_type not in ["LIP", "TC"]:
        experiment_type =  None

    target_folder = get_target_folder(
        user_folder=user_folder, 
        experiment_id=experiment_id, 
        experiment_type=experiment_type
    )
    
    from_directory = os.path.join(source, file_to_copy)
    to_directory = os.path.join(target_folder, file_to_copy)
    print(f"{datetime.datetime.now()} Copying {from_directory} to 
          {to_directory} {file_dict[file_to_copy]:.2f} MB")
    try:
        if os.path.isdir(from_directory):
            copytree(from_directory, to_directory)
        else:
            copyfile(from_directory, to_directory)
    except FileExistsError as f:
        print(f"File {file_to_copy} already exists.")


def get_files_from_target_folder(target_folder:str) -> list:
    # List to store all filenames
    file_list = []

    # Walk through all directories and subdirectories
    for root, dirs, files in os.walk(target_folder):
        for file in files:
            file_list.append(file)
    return file_list

def main():
    while True:
        now = datetime.datetime.now()
        this_month_ = f"{now.month}".zfill(2)
        this_year_ = now.year

        one_month_ago = one_month_ago = now - relativedelta(months=1)
        last_month_ = f"{one_month_ago.month}".zfill(2)
        last_month_year_ = one_month_ago.year

        # Folder Format 2402_data
        this_month_folder = str(this_year_)[2:4] + str(this_month_) + "_data"
        last_month_folder = str(last_month_year_)[2:4] + str(last_month_) + "_data"

        for month_folder in [this_month_folder, last_month_folder]:
            source = source_folder + month_folder
            sourcefiles = os.listdir(source)
            raw_files = [s for s in sourcefiles if s.endswith('.raw')]
            
            for user in user_folders.keys():
                print(f"{datetime.datetime.now()} checking raw files for {user} in {month_folder}.")
                user_raw_files = [x for x in raw_files if x.split('_')[2] == user]
                
                user_folder = user_folders[user]
                user_folder = nas_folder + user_folder
                target_files = get_files_from_target_folder(target_folder=user_folder)
                to_copy = [_ for _ in user_raw_files if _ not in target_files]

                print(f"FROM {source} TO {user_folder} FILES to copy: {len(to_copy)}")
                print(f"Waiting if file sizes are changing.")

                file_dict = {}

                for _ in to_copy:
                    file_dict[_] = get_full_size_mb(os.path.join(source, _))

                for i in tqdm(range(wait_time_size_change_sec*2)):
                    time.sleep(10)
                
                to_copy_ = []

                for _ in to_copy:
                    if get_full_size_mb(os.path.join(source, _)) == file_dict[_]:
                        if file_dict[_] > minimum_size_mb:
                            to_copy_.append(_)

                if len(to_copy) > 0:
                    for file in tqdm(to_copy_[::-1]):
                        copy_file(
                            file_to_copy=file, 
                            user_folder=user_folder,
                            source=source, 
                            file_dict=file_dict
                        )


if __name__ == "__main__":
    main()
