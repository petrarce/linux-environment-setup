#!/usr/bin/python3
import argparse
from git import Repo
import os
from sh import sed
from sh import realpath
import re

parser = argparse.ArgumentParser(
    prog = "Replace git patterns using the git tool",
    description="This prograp is used to find some epatterns and replace them with the"
    "specified exact pattern")
parser.add_argument("-f", "--from-pattern", required=True)
parser.add_argument("-t", "--to-pattern", required=True )
parser.add_argument("-p", "--repo-path", required=False, default=os.getcwd())

args = parser.parse_args()

fromPattern = args.from_pattern
toPattern = args.to_pattern
repoPath = re.sub(r'\s+', '', str(realpath([args.repo_path])))
if not os.path.isdir(repoPath):
    raise ValueError("path is not a directory", repoPath)

repo = Repo(repoPath, search_parent_directories=True)
git = repo.git

files = git.grep("--name-only", fromPattern)

for file in files.split():
    filePath = repoPath + "/" + file
    sed(["-E", "s," + fromPattern + "," + toPattern + ",g"], "-i", filePath)

