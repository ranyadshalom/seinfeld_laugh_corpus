"""
This is a crawler that downloads 'Big Bang Theory' screenplays.
"""
import re

import requests
from bs4 import BeautifulSoup

from seinfeld_laugh_corpus.corpus_creation.screenplay_downloader.screenplay_downloader import ScreenplayDownloader


def run(input_filename, output_filename):
    screenplay_downloader = SeinfeldScreenplayDownloader()
    screenplay_downloader.download(input_filename, output_filename)


class BbtScreenplayDownloader(ScreenplayDownloader):
    bbt_scripts_url = 'https://bigbangtrans.wordpress.com/'

    def _download_screenplay(self, season_num, episode_num, is_double_episode):
        screenplay_url = self._get_screenplay_url(season_num, episode_num)
        url_content = self._get_content(screenplay_url)

        # get text
        soup = BeautifulSoup(url_content, 'lxml')
        container = soup.find('div', class_='entrytext')
        list_of_paragraphs = container.find_all('p')
        screenplay_txt = "\n".join(p.get_text() for p in list_of_paragraphs)
        result = screenplay_txt
        return [result]

    def _get_screenplay_url(self, season_num, episode_num):
        episodes_list_page = self._get_content(self.bbt_scripts_url)
        soup = BeautifulSoup(episodes_list_page, 'lxml')
        sidebar = soup.find("div", id="sidebar")
        episode_tag = sidebar.find('a', string=re.compile("Series %.2d Episode %.2d" % (season_num, episode_num)))
        if not episode_tag and episode_tag.name != 'a':
            raise Exception("Screenplay not found in %s!" % self.bbt_scripts_url)
        return episode_tag['href']

    def _cleanup(self, screenplay_txt):
        lines = re.split(r"[\n\r\t]+", screenplay_txt)
        lines = [l for l in lines if not re.match('^Scene: ', l)]
        lines = [l for l in lines if l.strip()]
        lines = self._capitalize_all_character_names(lines)
        lines = lines[:-1] if "end" in lines[-1].lower() else lines
        return "\n" + "\n".join(lines)


if __name__ == '__main__':
    # test
    downloader = BbtScreenplayDownloader()

    print(downloader.download("S02E11.mkv", "S10E01.screenplay"))

