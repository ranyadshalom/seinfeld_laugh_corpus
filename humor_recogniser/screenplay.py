import re
from collections import namedtuple

Line = namedtuple('Line', ['character', 'txt', 'start', 'end', 'is_funny', 'laugh_time'])
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

    def __str__(self):
        return "S%.2dE%.2d %s" % (self.season, self.episode, self.episode_name)

    def __repr__(self):
        return "Screenplay('S%.2dE%.2d %s')" % (self.season, self.episode, self.episode_name)

    def fold_laughs(self):
        result = []
        for i, line in enumerate(self.lines):
            if i+1 < len(self.lines) and isinstance(self.lines[i+1], Laugh)\
                    and isinstance(line, Line):
                result.append(Line(character=line.character, txt=line.txt, start=line.start, end=line.end,
                                   is_funny=True, laugh_time=self.lines[i+1].time))
            elif isinstance(line, Laugh):
                pass
            else:
                result.append(line)
        self.lines = result

    @classmethod
    def from_file(cls, file_path, fold_laughs=False):
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
                                                     start=start, end=end, character=current_character,
                                                     is_funny=None, laugh_time=None))
        if fold_laughs:
            screenplay.fold_laughs()
        return screenplay
