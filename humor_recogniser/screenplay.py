import re
from collections import namedtuple

Line = namedtuple('Line', ['character', 'txt', 'start', 'end'])
Laugh = namedtuple('Laugh', ['time'])


class Screenplay:
    """
    Represents a Seinfeld screenplay in the memory.
    """
    def __init__(self, filename):
        self.lines = []
        self.filename = filename
        m = re.findall(r'\d+', filename)
        self.season, self.episode = int(m[0]), int(m[1])
        self.episode_name = filename[16:-7].replace('.', ' ')

    def __iter__(self):
        for line in self.lines:
            yield line

    def __getitem__(self, item):
        return self.lines[item]


    @classmethod
    def from_file(cls, file_path):
        filename = file_path.rsplit('/',1)[-1]
        screenplay = Screenplay(filename)


        with open(file_path, encoding='utf8', errors='ignore') as f:
            lines = f.__iter__()
            for line in lines:
                if line[0] == '#':
                    current_character = line.replace('#', '').strip()
                else:
                    start = float(line)
                    txt = lines.readline()
                    if '**LOL**' in txt:
                        screenplay.lines.append(Laugh(time=start))
                    else:
                        for i in range(3):
                            # maximum 3 lines in one subtitle
                            end = lines.readline()
                            try:
                                end = float(end)
                            except ValueError:
                                txt += ('\n'+end)
                            else:
                                break
                        screenplay.lines.append(Line(txt=txt.replace('\n', ' ').strip(),
                                                     start=start, end=end, character=current_character))
        return screenplay
