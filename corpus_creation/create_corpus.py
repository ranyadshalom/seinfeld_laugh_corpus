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
from corpus_creation.screenplay_downloader import screenplay_downloader

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
        self.filename = ntpath.basename(self.filepath)

    def process(self):
        try:
            print("Processing '%s'..." % self.filename)
            self._extract_audio()
            self._extract_laugh_track()
            self._extract_laughter_times()
            self._get_subtitles()
            self._get_screenplay()
            self._format_screemplay()
            merge(self.files['screenplay'], self.files['subtitles'], self.files['laughter_times'])
        except LaughExtractionException as e:
            print("ERROR for '%s': %s" % (self.filename, e))
        except SubtitlesNotInSyncException:
            print("ERROR for '%s': Subtitles not in sync." % self.filename)
        except ScreenplayParseException:
            print("ERROR for '%s': Screenplay parsing error." % self.filename)
        except MergeException:
            print("ERROR for '%s': Merging error." % self.filename)
        except Exception as e:
            print("ERROR for '%s': %s" % (self.filename, str(e)))
        else:
            print("SUCCESS for '%s'." % self.filename)
        finally:
            print("Cleaning up...")
            self._cleanup()

    def _extract_audio(self):
        print("Extracting audio...")
        # audio file name is the same as the video's but with .wav extension
        self.files['audio'] = self.filepath.rsplit(".", 1)[0] + '.wav'
        try:
            # ffmpeg will extract the audio in uncompressed PCM format.
            exit_code = subprocess.call([os.path.join(FFMPEG_PATH, 'ffmpeg.exe'), "-i", self.filepath,
                                         self.files['audio']])
            if exit_code != 0:
                raise Exception("ffmpeg exit code: %d. Your video file may be corrupted." % exit_code)
        except Exception as e:
            del files['audio']
            raise Exception("Make sure you have a working version of ffmpeg in the external_tools folder.\n%s" % str(e))

    def _extract_laugh_track(self):
        print("Extracting laugh track...")
        self.files['laugh_track'] = self.filepath.rsplit(".", 1)[0] + '_laugh.wav'

        try:
            exit_code = subprocess.call([os.path.join(SOX_PATH, 'sox.exe'), '--norm', self.files['audio'],
                                         self.files['laugh_track'], "oops"])
            if exit_code != 0:
                raise Exception("sox exit code: %d." % exit_code)
        except Exception as e:
            del files['laugh_track']
            raise Exception("Make sure you have a working version of sox in the external_tools folder.\n%s" % str(e))

    def _extract_laughter_times(self):
        print("Extracting laughter times...")
        self.files['laughter_times'] = self.files['laugh_track'].rsplit(".", 1)[0] + '.laugh'
        try:
            extract_laughter_times.run(input=self.files['laugh_track'], output=self.files['laughter_times'])
        except Exception as e:
            del self.files['laughter_times']
            raise LaughExtractionException(str(e))

    def _get_subtitles(self):
        print("Getting subtitles...")
        # audio file name is the same as the video's but with .wav extension
        self.files['subtitles'] = self.filepath.rsplit(".", 1)[0] + '.srt'
        try:
            # ffmpeg will extract the subtitles from the .mkv file.
            exit_code = subprocess.call([os.path.join(FFMPEG_PATH, 'ffmpeg.exe'), "-i", self.filepath, '-map', '0:s:0',
                                         self.files['subtitles']])
            if exit_code != 0:
                raise Exception("ffmpeg exit code: %d. Subtitles could not be extracted. Please make sure"
                                "that the .mkv file contains text subtitles and not bitmap subtitles." % exit_code)
        except Exception as e:
            del files['subtitle']
            raise Exception("Make sure you have a working version of ffmpeg in the external_tools folder.\n%s" % str(e))

    def _get_screenplay(self):
        print("Getting screenplay...")
        self.files['screenplay'] = self.filepath.rsplit(".", 1)[0] + '.screenplay'
        try:
            screenplay_downloader.run(input_filename=self.filename, output_filename=self.files['screenplay'])
        except Exception as e:
            del self.files['screenplay']
            raise Exception("Error getting screenplay: %s" % str(e))






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
