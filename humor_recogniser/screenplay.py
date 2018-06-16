from collections import namedtuple

Line = namedtuple('Line', ['character', 'txt', 'start', 'end'])
Laugh = namedtuple('Laugh', ['time'])


class Screenplay:
    """
    Represents a Seinfeld screenplay in the memory.
    """
    def __init__(self):
        self.lines = []

    def __iter__(self):
        for line in self.lines:
            yield line

    def __getitem__(self, item):
        return self.lines[item]

    @classmethod
    def from_file(cls, file_path):
        screenplay = Screenplay()

        with open(file_path) as f:
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
                        end = lines.readline()
                        try:
                            end = float(end)
                        except ValueError:
                            txt += ('\n'+end)
                            end = float(lines.readline())
                        screenplay.lines.append(Line(txt=txt.replace('\n', ' ').strip(),
                                                     start=start, end=end, character=current_character))
        return screenplay
