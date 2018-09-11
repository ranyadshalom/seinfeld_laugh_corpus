"""
This is a crawler that downloads screenplays from 'seinology.com' given the season and episode numbers.
"""
import re

import requests
from bs4 import BeautifulSoup

from seinfeld_laugh_corpus.corpus_creation.screenplay_downloader.screenplay_downloader import ScreenplayDownloader


def run(input_filename, output_filename):
    screenplay_downloader = SeinfeldScreenplayDownloader()
    screenplay_downloader.download(input_filename, output_filename)


class FriendsScreenplayDownloader(ScreenplayDownloader):
    friends_scripts_url = 'https://fangj.github.io/friends/season/'
    non_script_texts = ["transcribed by:", "written by:", "story by:", "teleplay by:", "aired:", "produced by:",
                        "minor adjustments by:", "with help from:", "htmled by:", "final check by:"]

    def _download_screenplay(self, season_num, episode_num, is_double_episode):
        screenplay_url = self._get_screenplay_url(season_num, episode_num)
        url_content = self._get_content(screenplay_url)

        # get text
        soup = BeautifulSoup(url_content, 'lxml')
        try:
            header = soup.find_all("hr", limit=2)[-1]
        except IndexError:
            header = soup.find("p", class_="scene")
        s = header.find_all_next("p")
        s = [tag for tag in s if not ('align' in tag.attrs or 'class' in tag.attrs)]
        screenplay_txt = "\n".join((line.get_text() for line in s if "transcribed by:" not in line.get_text().lower()))
        result = screenplay_txt

        if is_double_episode:
            return [result, self._download_screenplay(season_num, episode_num + 1, False)[0]]
        else:
            return [result]

    @staticmethod
    def _get_content(screenplay_url):
        retry_num = 0
        while True:
            r = requests.get(screenplay_url)
            if r.status_code == 200:
                break
            else:
                if retry_num > 3:
                    raise requests.HTTPError("Status code isn't 200")
                retry_num += 1
        return r.content

    def _get_screenplay_url(self, season_num, episode_num):
        return self.friends_scripts_url + "%02d%02d.html" % (season_num, episode_num)

    def _cleanup(self, screenplay_txt):
        lines = re.split(r"[\n\r\t]+", screenplay_txt)
        lines = [l for l in lines if l]
        lines = self._capitalize_all_character_names(lines)
        lines = lines[:-1] if "end" in lines[-1].lower() else lines
        return "\n".join(lines)


if __name__ == '__main__':
    # test
    downloader = FriendsScreenplayDownloader()

    print(downloader.download("S10E01.mkv", "S10E01.screenplay"))

