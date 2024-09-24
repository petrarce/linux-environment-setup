#!/usr/bin/python3

import argparse
import subprocess
import os

parser = argparse.ArgumentParser(
    prog="Remotely update irpu softfs",
    description="Update irpu softfs remotely")

parser.add_argument("-p", "--ssh-port", help="port for the rsync connection", required=False, default="22")
parser.add_argument("image_path", help="path to image")
parser.add_argument("host", help="host name")

args = parser.parse_args()
print(args)
imagePath = os.path.realpath(args.image_path)
imageName = os.path.basename(imagePath)
if not os.path.isfile(imagePath):
    raise RuntimeError(f"Invalid image path: {imagePath}")

# rsync image to host over ssh with rsync
try:
    subprocess.run(f"rsync -Plrz -e 'ssh -p {args.ssh_port}' {imagePath} {args.host}:/DATA/{imageName}", check=True, shell=True)
except:
    print("Failed to transfer file")
    exit(1)

try:
    subprocess.run(f"ssh -p {args.ssh_port} {args.host} ifus2shell.py -u admin -P update -d localhost /DATA/{imageName}", check=True, shell=True)
except:
    print("Failed to update image")
    exit(1)




