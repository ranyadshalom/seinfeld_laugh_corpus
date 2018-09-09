"""
This is a crawler that downloads screenplays from 'seinology.com' given the season and episode numbers.
"""
import re

import requests
from bs4 import BeautifulSoup

MIN_LENGTH = 13000  # if the screenplay has less characters, something is probably wrong.


class ScreenplayDownloader:
    def __init__(self):
        pass

    def run(self, input_filename, output_filename):
        self.download(input_filename, output_filename)

    def download(self, input_filename, output_filename):
        """
        Downloads the screenplay of a given episode.
        :param input_filename: The .mkv filename. Must contain season & episode numbers in the format S[int]E[int].
        :param output_filename: Output will be written to this file.
        :return:
        """
        result = ""
        season_num, episode_num, is_double_episode = self._parse_input_filename(input_filename)
        screenplay_txts = self._download_screenplay(season_num, episode_num, is_double_episode)
        for screenplay_txt in screenplay_txts:
            if len(screenplay_txt) < MIN_LENGTH:
                raise Exception("Something seems of with the screenplay. It's too short. Please check this manually.")
            screenplay_txt = self._cleanup(screenplay_txt)
            result += screenplay_txt + '\n'
        self._write_to_file(result, output_filename)

    @staticmethod
    def _parse_input_filename(input_filename):
        # The filename must contain the pattern 's[number]e[number]' denoting season and episode numbers for this to work.
        m = re.findall(r'\d+', input_filename)
        season_num = m[0]
        episode_num = m[1]
        if re.search(r'E\d+E\d+', input_filename):
            is_double_episode = True
        else:
            is_double_episode = False

        return int(season_num), int(episode_num), is_double_episode

    def _download_screenplay(self, season_num, episode_num, is_double_episode):
        raise NotImplementedError()

    def _cleanup(self, screenplay_txt):
        """
        Remove redundant text from the screenplay.
        """
        raise NotImplementedError()

    @staticmethod
    def _capitalize_all_character_names(lines):
        result = []
        for line in lines:
            if ":" in line[:16]:
                result.append(line.split(":")[0].upper().replace(" ", "") + ":" + ":".join(line.split(":")[1:]).lower())
            else:
                result.append(line)
        return result

    @staticmethod
    def _write_to_file(screenplay_txt, output):
        with open(output, 'w', encoding='utf8', errors='ignore') as f:
            f.write(screenplay_txt)

