"""
This is a crawler that downloads screenplays from 'seinology.com' given the season and episode numbers.
"""
from bs4 import BeautifulSoup
import requests
import re

SEINOLOGY_SCRIPTS_URL = "http://www.seinology.com/scripts-english.shtml"


def run(input_filename, output_filename):
    season_num, episode_num = parse_input_filename(input_filename)
    screenplay_txt = download_screenplay(season_num, episode_num)
    write_to_file(screenplay_txt, output_filename)


def parse_input_filename(input_filename):
    # The filename must contain the pattern 's[number]e[number]' denoting season and episode numbers for this to work.
    m = re.search(r'd+', input_filename)
    season_num = m.group(0)
    episode_num = m.group(1)
    return season_num, episode_num


def download_screenplay(season_num, episode_num):
    screenplay_url = get_screenplay_url(season_num, episode_num)

    return ''


def get_screenplay_url(season_num, episode_num):
    r = requests.get(SEINOLOGY_SCRIPTS_URL)
    if r.status_code != 200:
        raise requests.HTTPError("Status code isn't 200")

    soup = BeautifulSoup(r.content, parser='lxml')
    # TODO find the right episode in the web page