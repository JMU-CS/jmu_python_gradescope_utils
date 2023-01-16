#!/usr/bin/env python
"""Create an uploadable Gradescope zip file from an autograder folder.

usage: build_autograder.py [-h] [--output OUTPUT] folder

Command line tool for building Python autograders.

positional arguments:
  folder   Location of the folder containing autograder

optional arguments:
  -h, --help   show this help message and exit
  --output OUTPUT, -o OUTPUT
               Output zip file location
               (default is to store the file in the autograder folder).
"""

import argparse
from pathlib import Path
import jmu_gradescope_utils.build_utils as build_utils


def main():

    description = "Command line tool for building Python autograders."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('folder',
                        help='Location of the folder containing autograder')
    parser.add_argument('--output', '-o',
                        help="Output zip file location (default is to store the file in the autograder folder).")

    args = parser.parse_args()
    folder = Path(args.folder)
    if folder.exists():
        folder = folder.resolve()

    if args.output is None:
        args.output = str(folder / ('autograder_' + str(folder.name) + ".zip"))

    build_utils.build_zip(folder, args.output)


if __name__ == "__main__":
    main()
