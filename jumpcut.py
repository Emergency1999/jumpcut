import argparse

import os
import time

from videotools import *

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
parser.add_argument("-dm", "--debug_mode", type=bool, default=False, help="enables/disables debug information")

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
print(f"\nFinished in {Tnow} seconds")

#    f = open(DEBUG_FILE, "a")
#    f.write(f"{round(video_length/Tnow, 2):5.5}x speed: {round(Tnow, 2):8}s needed for {round(video_length, 2):8}s file: {INPUT_FILE}\n")
#    f.close()
