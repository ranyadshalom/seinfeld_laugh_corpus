from collections import namedtuple

Line = namedtuple('Line', ['character', 'txt', 'start', 'end'])
Laugh = namedtuple('Laugh', ['time'])


class Screenplay:
    def __init__(self):
        self.lines = []

    @classmethod
    def from_file(cls, file_path):
        screenplay = Screenplay()

        lines = f.__iter__()
        for line in lines:
            if line[0] == '#':
                current_character = line.replace('#', '').strip()
            else:
                start = float(line)
                txt = lines.next()
                if txt == '**LOL**':
                    screenplay.lines.append(Laugh(time=start))
                else:
                    end = lines.next()
                    try:
                        end = float(end)
                    except ValueError:
                        txt += ('\n'+end)
                        end = float(lines.next())
                    screenplay.lines.append(Line(txt=txt, start=start, end=end, character=current_character))




#
#    @classmethod
#    def from_file(cls, file_path):
#        screenplay = Screenplay()
#        line = '\n'
#
#        with open(file_path) as f:
#            while line:
#                line = f.readline()
#
#                if line[0] == '#':
#                    current_character = line.replace('#', '').strip()
#                else:
#                    start = float(line)
#                    txt = f.readline()
#                    if txt == '**LOL**':
#                        screenplay.lines.append(Laugh(time=start))
#                    else:
#                        end = f.readline()
#                        try:
#                            end = float(end)
#                        except ValueError:
#                            txt += ('\n'+end)
#                            end = float(f.readline())
#                        screenplay.lines.append(Line(txt=txt, start=start, end=end, character=current_character))
#
