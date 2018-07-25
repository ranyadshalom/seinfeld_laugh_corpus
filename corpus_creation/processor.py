import argparse
import os
import subprocess
import traceback
import ntpath

# internal imports
from laugh_extraction import extract_laughter_times
from screenplay_downloader import screenplay_downloader
from screenplay_formatter import screenplay_parser
from data_merger import data_merger
#from subtitle_getter import subtitle_getter
from subtitle_getter.subtitle_getter import SubtitlesNotInSyncException
from config import FFMPEG_PATH, SOX_PATH


def run(file_path, output_path):
    processor = Processor(file_path, output_path)
    processor.process()


class Processor:
    """
    A class that generates corpus data from a Seinfeld episode in the .mkv file format.
    """
    def __init__(self, filepath, outputpath):
        self.filepath = filepath      # path of the video file of the episode
        self.outputpath = outputpath  # path of the folder in which to write the output
        self.temp_files = {}               # paths of all the temporary files that will be used in the processing
        self.files_to_keep = []
        self.filename = ntpath.basename(self.filepath)
        self.merged_filename = self.filepath.rsplit(".", 1)[0] + '.merged'

    def process(self):
        try:
            if os.path.isfile(self.merged_filename):
                print("Skipping '%s' - file already exists." % self.merged_filename)
                return
            print("Processing '%s'..." % self.filename)
            self._extract_audio()
            self._normalize_audio()
            self._extract_laugh_track()
            self._extract_laughter_times()
            self._get_subtitles()
            self._get_screenplay()
            self._format_screenplay()
            self._merge_data()
        except LaughExtractionException as e:
            print("ERROR for '%s': Laugh extraction error. %s" % (self.filename, e))
            traceback.print_exc()
        except SubtitlesNotInSyncException:
            print("ERROR for '%s': Subtitles not in sync." % self.filename)
        except ScreenplayParseException:
            print("ERROR for '%s': Screenplay parsing error." % self.filename)
        except MergeException:
            print("ERROR for '%s': Merging error." % self.filename)
        except Exception as e:
            print("ERROR for '%s': %s" % (self.filename, str(e)))
            traceback.print_exc()
        else:
            print("SUCCESS for '%s'." % self.filename)
        finally:
            print("Cleaning up...")
            self._cleanup()

    def _extract_audio(self):
        print("Extracting audio...")
        # audio file name is the same as the video's but with .wav extension
        self.temp_files['audio'] = self.filepath.rsplit(".", 1)[0] + '.wav'
        try:
            # ffmpeg will extract the audio in uncompressed PCM format.
            exit_code = subprocess.call([os.path.join(FFMPEG_PATH, 'ffmpeg.exe'), "-i", self.filepath,
                                         self.temp_files['audio']], stdout=subprocess.DEVNULL)
            if exit_code != 0:
                raise Exception("ffmpeg exit code: %d. Your video file may be corrupted." % exit_code)
        except Exception as e:
            del self.temp_files['audio']
            raise Exception("Make sure you have a working version of ffmpeg in the external_tools folder.\n%s" % str(e))

    def _normalize_audio(self):
        print("Normalizing audio...")
        # audio file name is the same as the video's but with .wav extension
        self.temp_files['norm_audio'] = self.filepath.rsplit(".", 1)[0] + '_norm.wav'
        try:
            exit_code = subprocess.call([os.path.join(SOX_PATH, 'sox.exe'), self.temp_files['audio'],
                                         self.temp_files['norm_audio'], "gain", "-n"], stdout=subprocess.DEVNULL)
            if exit_code != 0:
                raise Exception("sox exit code: %d. Could not normalize audio." % exit_code)
        except Exception as e:
            del self.temp_files['norm_audio']
            raise Exception("Make sure you have a working version of sox in the external_tools folder.\n%s" % str(e))

    def _extract_laugh_track(self):
        print("Extracting laugh track...")
        self.temp_files['laugh_track'] = self.filepath.rsplit(".", 1)[0] + '_laugh.wav'

        try:
            exit_code = subprocess.call([os.path.join(SOX_PATH, 'sox.exe'), self.temp_files['norm_audio'],
                                         self.temp_files['laugh_track'], "oops"], stdout=subprocess.DEVNULL)
            if exit_code != 0:
                raise Exception("sox exit code: %d." % exit_code)
        except Exception as e:
            del self.temp_files['laugh_track']
            raise Exception("Make sure you have a working version of sox in the external_tools folder.\n%s" % str(e))

    def _extract_laughter_times(self):
        print("Extracting laughter times...")
        self.temp_files['laughter_times'] = self.temp_files['laugh_track'].rsplit(".", 1)[0] + '.laugh'
        try:
            extract_laughter_times.run(input=self.temp_files['laugh_track'], output=self.temp_files['laughter_times'])
        except Exception as e:
            del self.temp_files['laughter_times']
            raise LaughExtractionException(str(e))

    def _get_subtitles(self):
        print("Getting subtitles...")
        # audio file name is the same as the video's but with .wav extension
        self.temp_files['subtitles'] = self.filepath.rsplit(".", 1)[0] + '.srt'
        try:
            subtitle_getter.run(self.filepath, self.temp_files['audio'], self.temp_files['subtitles'],)
        except Exception as e:
            del self.temp_files['subtitles']
            raise Exception("Error getting subtitles: %s" % str(e))

    def _get_screenplay(self):
        print("Getting screenplay...")
        self.temp_files['screenplay'] = self.filepath.rsplit(".", 1)[0] + '.screenplay'
        try:
            screenplay_downloader.run(input_filename=self.filename, output_filename=self.temp_files['screenplay'])
        except Exception as e:
            del self.temp_files['screenplay']
            raise Exception("Error getting screenplay: %s" % str(e))

    def _format_screenplay(self):
        print("Formatting & parsing screenplay...")
        self.temp_files['formatted_screenplay'] = self.filepath.rsplit(".", 1)[0] + '.formatted'
        try:
            screenplay_parser.run(self.temp_files['screenplay'], self.temp_files['formatted_screenplay'])
        except Exception as e:
            del self.temp_files['formatted_screenplay']
            raise Exception("Error formatting and parsing screenplay: %s" % str(e))

    def _merge_data(self):
        print("Merging all data to one file (this will take a while)...")
        merged_filename = self.filepath.rsplit(".", 1)[0] + '.merged'
        data_merger.run(self.temp_files['formatted_screenplay'], self.temp_files['subtitles'],
                        self.temp_files['laughter_times'], merged_filename)

    def _cleanup(self):
        for key, filename in self.temp_files.items():
            if key not in self.files_to_keep:
                os.remove(filename)
                print("Removed '%s'" % filename)


class LaughExtractionException(Exception):
    pass


class ScreenplayParseException(Exception):
    pass


class MergeException(Exception):
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process 1 Seinfeld episode video file and create a .merged corpus file.")
    parser.add_argument('video_file', help='Path to the video file')
    parser.add_argument('output_path', help='Output will be written to this path.')
    args = parser.parse_args()
    video_file = args.video_file
    output_path = args.output_path

    if not os.path.exists(video_file):
        print("'%s' illegal path!\n" % episodes_path)
    elif not os.path.isdir(output_path):
        print("'%s' is not a directory!" % output_path)

    run(video_file, output_path)
