"""
A module that creates the annotated Seinfeld corpus from scratch, given the episodes in .mkv format.
"""

# python imports
import argparse
import os
import psutil
import subprocess

# internal imports
from processor import Processor


def run(episodes_path, output_path):
    for dirpath, _, filenames in os.walk(episodes_path):
        for filename in filenames:
            if filename.endswith(".mkv"):
                print(psutil.virtual_memory())
                file_path = os.path.join(dirpath, filename)
                subprocess.call(['python', 'processor.py', file_path, output_path])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A script to create the Seinfeld corpus from scratch.")
    parser.add_argument('episodes_path', help='A folder that contains all of the Seinfeld episodes in .mkv format.')
    parser.add_argument('output_path', help='Output will be written to this path.')
    args = parser.parse_args()
    episodes_path = args.episodes_path
    output_path = args.output_path

    if not os.path.exists(episodes_path):
        print("'%s' illegal path!\n" % episodes_path)
    elif not os.path.isdir(output_path):
        print("'%s' is not a directory!" % output_path)

    run(episodes_path, output_path)
