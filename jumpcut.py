import argparse

import os
import time
import shutil

from silencer import *


def deletePath(s):
    try:
        shutil.rmtree(s, ignore_errors=False)
    except OSError:
        print(f"Deletion of the directory {s} failed")
        print(OSError)


def createPath(s):
    if os.path.exists(s):
        deletePath(s)
    try:
        os.mkdir(s)
    except OSError:
        assert False, f"Creation of the directory {s} failed. (The TEMP folder may already exist. Delete or rename it, and try again.)"


def output_name(name):
    dotIndex = name.rfind(".")
    return name[:dotIndex] + "_ALTERED" + name[dotIndex:]


class Video:
    def __init__(self, input_file, output_path="", input_path="", output_file=None):
        self.input_file = input_file
        if output_file:
            self.output_file = output_file
        else:
            self.output_file = input_file[0:-4] + "_sil.mp4"
        self.input_path = input_path
        self.output_path = output_path
        self.temp_folder = "TEMP_" + input_file[:-4] + "/"
        createPath("TEMP_" + input_file[:-4])
        self.video_length = get_video_length(input_path + input_file)
        self.arr_silence_ms = []
        self.arr_audio_s = []
        self.start_time = None

    def __del__(self):

        deletePath(self.temp_folder)
        # deleting Temp folder

    def extract_audio(self):
        ffmpeg_get_audio(self.input_path + self.input_file, self.temp_folder + "audio.wav")

    def detect_silence(self):
        self.arr_silence_ms = silencer(self.temp_folder + "audio.wav", DCB_THRESHOLD, SILENT_LENGTH, SEEK_STEP)
        self.arr_silence_ms.append((self.video_length, self.video_length))

    def create_arr_audio_s(self):
        last = 0.0
        for x, y in self.arr_silence_ms:
            start = last
            end = x / 1000
            if end - start > 0.01:
                start = max(start - KEEP_SILENCE, 0)
                end = min(end + KEEP_SILENCE, self.video_length)
                self.arr_audio_s.append((round(start, 3), round(end, 3)))
            last = y / 1000

    def cut_array(self):
        ffmpeg_cut_array(file_input=self.input_path + self.input_file,
                         file_output=self.output_path + self.output_file
                         , temp_file=self.temp_folder + "script.txt", timearray=self.arr_audio_s)

    def work(self):
        self.start_time = time.time()
        self.extract_audio()
        self.detect_silence()
        self.create_arr_audio_s()
        self.cut_array()
        self.debugger()

    def debugger(self):
        if DEBUG_MODE:
            Tnow = time.time() - self.start_time
            print("Output debug information")
            f = open('debug.txt', 'a+')
            f.write(
                f"{round(self.video_length / Tnow, 2):5.5}x speed: {round(Tnow, 2):8}s needed for {round(self.video_length, 2):8}s file: {self.input_path}{self.input_file}\n")
            f.close()

# -------------------------------------------------- ARGS

parser = argparse.ArgumentParser(description="Modifies a video file to cut out silence.")
parser.add_argument("-i", "--input_file", type=str, help="the video file you want modified")
parser.add_argument("-o", "--output_file", type=str, help="the output file")
parser.add_argument("-ip", "--input_path", type=str, default="INPUT/", help="the input directory")
parser.add_argument("-op", "--output_path", type=str, default="OUTPUT/", help="the Output directory")
parser.add_argument("-d", "--dcb_threshold", type=int, default=10, help="the threshold accepted as \"silence\" in dcb")
parser.add_argument("-k", "--keep_silence", type=float, default=0.2,
                    help="amount of distance from silence to audio in s")
parser.add_argument("-l", "--silent_length", type=int, default=500, help="the miminum amount of silence in ms")
parser.add_argument("-s", "--seek_step", type=int, default=10, help="the audio step size in ms")
parser.add_argument("-dm", "--debug_mode", type=bool, default= False, help="enables/disables debug information")

args = parser.parse_args()
INPUT_DIR = args.input_path
OUTPUT_DIR = args.output_path
INPUT_FILE = args.input_file
OUTPUT_FILE = args.output_file
DCB_THRESHOLD = args.dcb_threshold
KEEP_SILENCE = args.keep_silence
SILENT_LENGTH = args.silent_length
SEEK_STEP = args.seek_step
INPUT_FILES_NAMES = os.listdir(INPUT_DIR)
DEBUG_MODE = args.debug_mode
OUTPUT_FILES_NAMES = []

assert (INPUT_FILE is not None) or (len(INPUT_FILES_NAMES) > 0), "why u put no input file-s, that dum"

t = time.time()
# --------------------------------------- creates arr of Vid class
video_arr = []
if INPUT_FILE is not None:
    video_arr.append(Video(input_file=INPUT_FILE, output_file=OUTPUT_FILE))

elif len(INPUT_FILES_NAMES) > 0:
    for input_filename in INPUT_FILES_NAMES:
        video_arr.append(Video(input_file=input_filename, output_path=OUTPUT_DIR, input_path=INPUT_DIR))

for vid in video_arr:
    vid.work()

Tnow = time.time() - t
print("\nfinished in %f seconds" % (Tnow))
