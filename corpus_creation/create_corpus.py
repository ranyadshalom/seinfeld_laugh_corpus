import argparse


def run(episodes_path):
    # for each episode:
    #   extract .wav audio
    #   extract audience recording
    #   if audience recording is valid:
    #       extract laughter times
    #       download subtitles
    #           while subtitles don't match
    #               try another subtitle file (max retries: 4)
    #           if not found: quit
    #       download screenplay
    #       parse screenplay
    #       merge laughter_times, screenplay, subtitles


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A script to create the Seinfeld corpus from scratch.")
    parser.add_argument('episodes_path', help='A folder that contains all of the Seinfeld episodes in .mkv format.')
    args = parser.parse_args()
    episodes_path = args.episodes_path

    if not os.path.exists(episodes_path):
        print("'%s' illegal path!\n" % output)
    else:
        run(episodes_path)
