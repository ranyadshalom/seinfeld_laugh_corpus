"""
By Ran Yad-Shalom
17.9.2018
"""

import argparse
import re

from .seinfeld_screenplay_parser import SeinfeldScreenplayParser


def run(src, dst):
    p = FriendsScreenplayParser()
    p.to_file(src, dst)


class BbtScreenplayParser(SeinfeldScreenplayParser):
    """Big Band Theory screenplay parser"""


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert screenplays from seinfeldscripts.com to a single digestable format.")
    parser.add_argument('input', help='A .txt file of a seinfeld screenplay from seinfeldscripts.com')
    parser.add_argument('output', help='Destination .txt file.')
    args = parser.parse_args()
    src, dst = args.input, args.output

    run(src, dst)

