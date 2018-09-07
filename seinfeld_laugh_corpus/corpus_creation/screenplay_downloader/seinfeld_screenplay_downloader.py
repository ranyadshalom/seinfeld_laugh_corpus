"""
This is a crawler that downloads screenplays from 'seinology.com' given the season and episode numbers.
"""
import re

import requests
from bs4 import BeautifulSoup

from .screenplay_downloader import ScreenplayDownloader

SEINOLOGY_SCRIPTS_URL = "http://www.seinology.com/scripts/"
EPISODES_PER_SEASON = [5, 12, 23, 24, 22, 24, 24, 22, 24]
episodes_per_season_commulative = [sum(EPISODES_PER_SEASON[:i]) for i in range(len(EPISODES_PER_SEASON))]


def run(input_filename, output_filename):
    screenplay_downloader = SeinfeldScreenplayDownloader()
    screenplay_downloader.download(input_filename, output_filename)


class SeinfeldScreenplayDownloader(ScreenplayDownloader):
    def _download_screenplay(self, season_num, episode_num, is_double_episode):
        screenplay_url = self._get_screenplay_url(season_num, episode_num)

        retry_num = 0
        while True:
            r = requests.get(screenplay_url)
            if r.status_code == 200:
                break
            else:
                if is_double_episode:
                    screenplay_url = self._get_screenplay_url_double_episode(season_num, episode_num)
                    is_double_episode = False  # Some episodes are split in the website, but not in the DVD, and vice versa.
                if retry_num > 3:
                    raise requests.HTTPError("Status code isn't 200")
                retry_num += 1

        # get text
        soup = BeautifulSoup(r.content, 'html.parser')
        s = soup.find("td", class_="spacer2")
        screenplay_txt = s.get_text()
        # TODO clean up txt for formatting
        result = screenplay_txt

        if is_double_episode:
            return [result, self._download_screenplay(season_num, episode_num + 1, False)[0]]
        else:
            return [result]

    @staticmethod
    def _get_screenplay_url(season_num, episode_num):
        page_number = episodes_per_season_commulative[season_num - 1] + episode_num
        return SEINOLOGY_SCRIPTS_URL + "/script-%02d.shtml" % page_number

    @staticmethod
    def _get_screenplay_url_double_episode(season_num, episode_num):
        page_number = episodes_per_season_commulative[season_num - 1] + episode_num
        return SEINOLOGY_SCRIPTS_URL + ("/script-%02dand%02d.shtml" % (page_number, page_number+1))

