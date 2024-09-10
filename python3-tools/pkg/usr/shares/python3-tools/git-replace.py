#!/usr/bin/python3
import argparse
import os
import re
from sh import sed
from sh import realpath
from git import Repo

parser = argparse.ArgumentParser(
    prog="git-replace",
    description="Used to replace string patterns within the files in the git repository with the replacement string",
)

parser.add_argument("-b", "--before-pattern", required=True)
parser.add_argument("-a", "--after-pattern", required=True)
parser.add_argument("-p", "--repo-path", required=False, default=os.getcwd())
parser.add_argument("-f", "--files", action="store_true")

args = parser.parse_args()

beforePattern = args.before_pattern
afterPattern = args.after_pattern
targetPath = re.sub(r"\s+", "", str(realpath([args.repo_path])))
renameFiles = args.files

if not os.path.isdir(targetPath):
    raise ValueError("path is not a directory", targetPath)

repo = Repo(targetPath, search_parent_directories=True)
repoPath = os.path.realpath(repo.git.rev_parse("--show-toplevel"))

if not renameFiles:
    try:
        files = repo.git.grep("--name-only", beforePattern, "--", targetPath)
        for file in files.split():
            filePath = repoPath + "/" + file
            sed(
                ["-E", "s," + beforePattern + "," + afterPattern + ",g"], "-i", filePath
            )
    except Exception as err:
        print("Cannot substitute pattern:", beforePattern, err)


else:
    try:
        files = repo.git.ls_files(targetPath)
        for file in files.split():
            match = re.search(beforePattern, file, re.RegexFlag.DEBUG)
            if not match is None:
                newFile = re.sub(beforePattern, afterPattern, file)
                repo.git.mv(file, newFile)
    except Exception as err:
        print("Cannot renamie files with pattern:", beforePattern, err)
