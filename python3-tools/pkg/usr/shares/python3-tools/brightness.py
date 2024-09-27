#!/usr/bin/python3
import os
import subprocess
import argparse

parser = argparse.ArgumentParser(
    prog="brightness",
    description="The application for setting and updating the screen brightness"
)

parser.add_argument(
    "-l", "--list-displays", action="store_true", help="List available display names"
)
parser.add_argument(
    "-t",
    "--target-display",
    default=None,
    required=False,
    help="Set the display name. Use --list-displays for overview"
)
parser.add_argument(
    "-s",
    "--set",
    default=None,
    type=float,
    help="Set the brightness value. Should be between [0, 1]"
)
parser.add_argument(
    "-a",
    "--add",
    default=None,
    type=float,
    help="Increase/decrease current value of the brightness to the specified value."
)

args = parser.parse_args()

listDisplaysCommand = (
    "xrandr --listmonitors | grep -E \"^\s+[0-9]+\:\" | awk '{print $NF}'"
)

if args.list_displays:
    result = subprocess.run(
        listDisplaysCommand,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        text=True
    )
    if result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode,
            listDisplaysCommand,
            output=result.stdout,
            stderr=result.stderr
        )
    print(result.stdout, result.stderr)
    exit(0)

targetDisplay = args.target_display
absValue = args.set
relValue = args.add

if absValue == None and relValue == None:
    parser.print_help()
    raise ValueError("Either --set or --add should be specified")

if targetDisplay == None:
    result = subprocess.run(
        listDisplaysCommand,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        text=True,
    )
    if result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode,
            listDisplaysCommand,
            output=result.stdout,
            stderr=result.stderr
        )
    displays = result.stdout.split()
    if len(displays) == 0:
        raise ValueError("No displays available")
    targetDisplay = displays[0]

if absValue != None:
    value = min([max([float(absValue), 0.1]), 1])
    subprocess.run(f"xrandr --output {targetDisplay} --brightness {value}", shell=True)

elif relValue:
    value = float(relValue)
    result = subprocess.run(
        f"xrandr  --verbose | pcregrep -M \"^{targetDisplay}(.*\n)*?\S\" | grep -vE \"^\S\" | grep -E Brightness | awk" + " '{print $NF}'",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    currentBrightness = float(result.stdout)
    newBrightness = min([max([currentBrightness + value, 0.1]), 1])
    subprocess.run(f"xrandr --output {targetDisplay} --brightness {newBrightness}", shell=True)
