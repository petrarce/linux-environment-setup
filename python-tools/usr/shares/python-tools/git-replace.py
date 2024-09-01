#!/usr/bin/python3
import argparse
import os
import re
from sh import sed
from sh import realpath
from git import Repo

parser = argparse.ArgumentParser(
    prog = "Replace git patterns using the git tool",
    description="This prograp is used to find some epatterns and replace them with the"
    "specified exact pattern")

parser.add_argument("-b", "--before-pattern", required=True)
parser.add_argument("-a", "--after-pattern", required=True )
parser.add_argument("-p", "--repo-path", required=False, default=os.getcwd())
parser.add_argument("-f", "--files", action="store_true")

args = parser.parse_args()

beforePattern = args.before_pattern
afterPattern = args.after_pattern
repoPath = re.sub(r'\s+', '', str(realpath([args.repo_path])))
renameFiles = args.files

if not os.path.isdir(repoPath):
    raise ValueError("path is not a directory", repoPath)

repo = Repo(repoPath, search_parent_directories=True)


if not renameFiles:
    try:
        files = repo.git.grep("--name-only", beforePattern)
        for file in files.split():
            filePath = repoPath + "/" + file
            sed(["-E", "s," + beforePattern + "," + afterPattern + ",g"], "-i", filePath)
    except Exception as err:
        print("Cannot substitute pattern:", beforePattern, err)


else:
    try:
        files = repo.git.ls_files()
        for file in files.split():
            match = re.search(beforePattern, file, re.RegexFlag.DEBUG)
            if not match is None:
                newFile = re.sub(beforePattern, afterPattern, file)
                repo.git.mv(file, newFile)
    except Exception as err:
        print("Cannot renamie files with pattern:", beforePattern, err)
