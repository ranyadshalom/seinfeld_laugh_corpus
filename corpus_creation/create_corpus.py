"""
A module that creates the annotated Seinfeld corpus from scratch, given the episodes in .mkv format.
"""

# python imports
import argparse
import os
import subprocess
import ntpath

# internal imports
from corpus_creation.laugh_extraction import extract_laughter_times


FFMPEG_PATH = os.path.join("external_tools", "ffmpeg", "bin")
SOX_PATH = os.path.join("external_tools", "sox")


def run(episodes_path, output_path):
    for dirpath, _, filenames in os.walk(episodes_path):
        for filename in filenames:
            if filename.endswith(".mkv"):
                file_path = os.path.join(dirpath, filename)
                processor =Processor(file_path, output_path)
                processor.process()


class Processor:
    """
    A class that generates corpus data from a Seinfeld episode in the .mkv file format.
    """
    def __init__(self, filepath, outputpath):
        self.filepath = filepath      # path of the video file of the episode
        self.outputpath = outputpath  # path of the folder in which to write the output
        self.files = {}               # paths of all the temporary files that will be used in the processing

    def process(self):
        filename = ntpath.basename(self.filepath)
        try:
            print("Processing '%s'..." % filename)
            self._extract_audio()
            self._extract_laugh_track()
            self._extract_laughter_times()
            self.files['laughter_times'] = self._extract_laughter_times(audio_filepath)
            self.files['subtitles'] = get_subtitles(filepath, audio_filepath)
            self.files['screenplay'] = get_screenplay(filename)
            merge(self.files['screenplay'], self.files['subtitles'], self.files['laughter_times'])
        except LaughExtractionException as e:
            print("ERROR for '%s': %s" % (filename, e))
        except SubtitlesNotInSyncException:
            print("ERROR for '%s': Subtitles not in sync." % filename)
        except ScreenplayParseException:
            print("ERROR for '%s': Screenplay parsing error." % filename)
        except MergeException:
            print("ERROR for '%s': Merging error." % filename)
        except Exception as e:
            print("ERROR for '%s': %s" % (filename, str(e)))
        else:
            print("SUCCESS for '%s'." % filename)
        finally:
            print("Cleaning up...")
            self._cleanup()

    def _extract_audio(self):
        # audio file name is the same as the video's but with .wav extension
        self.files['audio'] = self.filepath.rsplit(".", 1)[0] + '.wav'
        try:
            # ffmpeg will extract the audio in uncompressed PCM format.
            exit_code = subprocess.call([os.path.join(FFMPEG_PATH, 'ffmpeg.exe'), "-i", self.filepath,
                                         self.files['audio']])
            if exit_code != 0:
                raise Exception("ffmpeg exit code: %d. Your video file may be corrupted." % exit_code)
        except Exception as e:
            raise Exception("Make sure you have a working version of ffmpeg in the external_tools folder.\n%s" % str(e))

    def _extract_laugh_track(self):
        self.files['laugh_track'] = self.filepath.rsplit(".", 1)[0] + '_laugh.wav'

        try:
            exit_code = subprocess.call([os.path.join(SOX_PATH, 'sox.exe'), '--norm', self.files['audio'],
                                         self.files['laugh_track'], "oops"])
            if exit_code != 0:
                raise Exception("sox exit code: %d." % exit_code)
        except Exception as e:
            raise Exception("Make sure you have a working version of sox in the external_tools folder.\n%s" % str(e))

    def _extract_laughter_times(self):
        self.files['laughter_times'] = self.files['laugh_track'].rsplit(".", 1)[0] + '.laugh'
        try:
            extract_laughter_times.run(input=self.files['laugh_track'], output=self.files['laughter_times'])
        except Exception as e:
            del self.files['laughter_times']
            raise LaughExtractionException(str(e))

        # verify laughter times were indeed extracted
        # TODO case where there is spillage of audio from the episode to audience mics.



    def _cleanup(self):
        for filename in self.files.values():
            os.remove(filename)
            print("Removed '%s'" % filename)






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


class LaughExtractionException(Exception):
    pass


class SubtitlesNotInSyncException(Exception):
    pass


class ScreenplayParseException(Exception):
    pass


class MergeException(Exception):
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A script to create the Seinfeld corpus from scratch.")
    parser.add_argument('episodes_path', help='A folder that contains all of the Seinfeld episodes in .mkv format.')
    parser.add_argument('output_path', help='Output will be written to this path.')
    args = parser.parse_args()
    episodes_path = args.episodes_path
    output_path = args.output_path

    if not os.path.exists(episodes_path):
        print("'%s' illegal path!\n" % episodes_path)
    elif not os.path.isdir(output_path):
        print("'%s' is not a directory!" % output_path)
    else:
        run(episodes_path, output_path)
