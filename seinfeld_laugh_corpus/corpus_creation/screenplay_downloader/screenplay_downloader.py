"""
This is a crawler that downloads screenplays from 'seinology.com' given the season and episode numbers.
"""
import re

import requests
from bs4 import BeautifulSoup

MIN_LENGTH = 13000  # if the screenplay has less characters, something is probably wrong.
SEINOLOGY_SCRIPTS_URL = "http://www.seinology.com/scripts/"
EPISODES_PER_SEASON = [5, 12, 23, 24, 22, 24, 24, 22, 24]
episodes_per_season_commulative = [sum(EPISODES_PER_SEASON[:i]) for i in range(len(EPISODES_PER_SEASON))]


def run(input_filename, output_filename):
    result = ""
    season_num, episode_num, is_double_episode = parse_input_filename(input_filename)
    screenplay_txts = download_screenplay(season_num, episode_num, is_double_episode)
    for screenplay_txt in screenplay_txts:
        if len(screenplay_txt) < MIN_LENGTH:
            raise Exception("Something seems of with the screenplay. It's too short. Please check this manually.")
        screenplay_txt = cleanup(screenplay_txt)
        result += screenplay_txt + '\n'
    write_to_file(result, output_filename)


def parse_input_filename(input_filename):
    # The filename must contain the pattern 's[number]e[number]' denoting season and episode numbers for this to work.
    m = re.findall(r'\d+', input_filename)
    season_num = m[0]
    episode_num = m[1]
    if re.search(r'E\d+E\d+', input_filename):
        is_double_episode = True
    else:
        is_double_episode = False

    return int(season_num), int(episode_num), is_double_episode


def download_screenplay(season_num, episode_num, is_double_episode):
    screenplay_url = get_screenplay_url(season_num, episode_num)

    retry_num = 0
    while True:
        r = requests.get(screenplay_url)
        if r.status_code == 200:
            break
        else:
            if is_double_episode:
                screenplay_url = get_screenplay_url_double_episode(season_num, episode_num)
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
        return [result, download_screenplay(season_num, episode_num + 1, False)[0]]
    else:
        return [result]


def get_screenplay_url(season_num, episode_num):
    page_number = episodes_per_season_commulative[season_num - 1] + episode_num
    return SEINOLOGY_SCRIPTS_URL + "/script-%02d.shtml" % page_number


def get_screenplay_url_double_episode(season_num, episode_num):
    page_number = episodes_per_season_commulative[season_num - 1] + episode_num
    return SEINOLOGY_SCRIPTS_URL + ("/script-%02dand%02d.shtml" % (page_number, page_number+1))


def cleanup(screenplay_txt):
    """
    Remove redundant text from the screenplay.
    """
    # split lines
    lines = re.split(r"[\n\r\t]+", screenplay_txt)
    lines = [l for l in lines if l]
    # capitalize all character names (in case script has characters like 'Mr. VISAKI')
    lines = capitalize_all_character_names(lines)
    # cut out irrelevant part
    upper_delimiter = [delim for delim in lines if "===" in delim]
    upper_delimiter_i = lines.index(upper_delimiter[0]) + 1
    lower_delimiter_i = len(lines)-1 if "end" in lines[-1].lower() else len(lines)
    return "\n".join(lines[upper_delimiter_i:lower_delimiter_i])


def capitalize_all_character_names(lines):
    result = []
    for line in lines:
        if ":" in line[:16]:
            result.append(line.split(":")[0].upper().replace(" ", "") + ":" + ":".join(line.split(":")[1:]).lower())
        else:
            result.append(line)
    return result


def write_to_file(screenplay_txt, output):
    with open(output, 'w', encoding='utf8', errors='ignore') as f:
        f.write(screenplay_txt)

