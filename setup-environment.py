#!/usr/bin/python3
import os
import argparse
import re
import shutil

import datetime
from sh import tar


def list_files(path, recursive=True):
    files_list_tree = []

    for root, dirs, files in os.walk(environmentSourcePath):
        for file in files:
            files_list_tree.append(os.path.realpath(root + "/" + file))

    return files_list_tree

parser = argparse.ArgumentParser(
    prog="setup_environment.sh",
    description="Execute user environment setup routines for fetching/storing "
                "environment configurations from/to user environment to/from source repository"
)
parser.add_argument(
    "-n", "--no-backup",
    action="store_true",
    help="If flag is used the script will collect all files"
        "that are going to be substituted and store pack them into the archive"
        "Relevant only if -l is NOT set",
    required=False
)
parser.add_argument(
    "-l", "--load",
    action="store_true",
    help="Flag specifies if the files from reposytory should be updated from files, "
         "that are in current user environment, if not set the user environment will "
         "be updated with the files from repository."
)

parser.add_argument(
    "-i", "--install-deb",
    action="store_true",
    help=f"If flag is specified the script will install the deb packages with the "
         f"system package manager. Otherwice, content of the deb packages will be "
         f"installed under {os.getenv('HOME')}/apps"
)

# arg results
args = parser.parse_args()
load = args.load
install_deb = args.install_deb
no_backup = args.no_backup

# --- Start script logic ---
environmentSourcePath = f"{os.path.dirname(os.path.realpath(__file__))}/environment"
homePath = os.getenv("HOME")

filesMap = [
    {"repo": f, "env": re.sub(f"^{environmentSourcePath}", f"{homePath}", f)}
    for f in list_files(environmentSourcePath)
]


if load:
    for repoVsEnv in filesMap:
        shutil.copy(repoVsEnv["env"], repoVsEnv["repo"])
else:
    if not no_backup:
        filesUser = [ m["env"] for m in filesMap]
        formatted_date = datetime.datetime(1, 1, 1).today().strftime("%Y-%m-%d-%H-%M-%S")
        tar("--ignore-failed-read", "-cf", f"{homePath}/backup_{formatted_date}.tar",  filesUser)
    for m in filesMap:
        repo = m["repo"]
        env = m["env"]
        if os.path.isdir(env):
            print(f"[WARNING] omitting {env} since it is a directory")
            continue
        if os.path.exists(env):
            os.remove(env)
        
        if not os.path.exists(os.path.dirname(env)):
            os.makedirs(os.path.dirname(env))

        shutil.copy(repo, env)