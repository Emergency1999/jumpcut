import os
import time
import argparse

from videotools import *

# -------------------------------------------------- ARGS

parser = argparse.ArgumentParser(description="Modifies a video file to cut out silence.")
parser.add_argument("-i", "--input_file", type=str, help="the video file you want modified")
parser.add_argument("-o", "--output_file", type=str, help="the output file")
parser.add_argument("-id", "--input_directory", type=str, default="INPUT/", help="the input directory, needs to end with \"/\"")
parser.add_argument("-od", "--output_directory", type=str, default="OUTPUT/", help="the output directory, needs to end with \"/\"")
parser.add_argument("-a", "--output_append", type=str, default="_cut", help="changes the ending of outputfile if desired, \".\" means none")
parser.add_argument("-t", "--temp_directory", type=str, default="TEMP/", help="the temp directory, needs to end with \"/\"")

parser.add_argument("-d", "--dcb_threshold", type=int, default=10, help="the threshold accepted as \"silence\" in dcb")
parser.add_argument("-k", "--keep_silence", type=float, default=200, help="amount of distance from silence to audio in ms")
parser.add_argument("-l", "--silent_length", type=int, default=500, help="the miminum amount of silence in ms")
parser.add_argument("-s", "--seek_step", type=int, default=10, help="the audio step size in ms")
parser.add_argument("-c", "--chunksize", type=int, default=200, help="the videopart chunk size in seconds which the video is split before cutting")
parser.add_argument("-dm", "--debug_mode", type=str, default="", help="enables debug information to file given")

args = parser.parse_args()
INPUT_FILE = args.input_file
OUTPUT_FILE = args.output_file
INPUT_DIR = args.input_directory
OUTPUT_DIR = args.output_directory
OUTPUT_APPEND = args.output_append
TEMP_DIR = args.temp_directory

DCB_THRESHOLD = args.dcb_threshold
KEEP_SILENCE = args.keep_silence / 1000
SILENT_LENGTH = args.silent_length
SEEK_STEP = args.seek_step
CHUNKSIZE = args.chunksize

INPUT_FILES_NAMES = os.listdir(INPUT_DIR)
DEBUG_MODE = args.debug_mode
OUTPUT_FILES_NAMES = []

assert (INPUT_FILE is not None) or (len(INPUT_FILES_NAMES) > 0), "why u put no input file, that dum"
OUTPUT_APPEND = OUTPUT_APPEND == "." if "" else OUTPUT_APPEND

t = time.time()
# -------------------------------------------------- creates arr of Vid class

video_arr = []
def add_video(input_file, output_file, temp_folder):
    video_arr.append(Videocutter(   input_file=input_file, 
                                    output_file=output_file, 
                                    dcb_threshold=DCB_THRESHOLD, 
                                    keep_silence=KEEP_SILENCE, 
                                    silent_length=SILENT_LENGTH, 
                                    seek_step=SEEK_STEP, 
                                    temp_folder=temp_folder, 
                                    chunksize=CHUNKSIZE, 
                                    debug_mode=DEBUG_MODE))


if INPUT_FILE is not None:
    # Filemode
    if OUTPUT_FILE is None:
        OUTPUT_FILE = customize_filename(INPUT_FILE, OUTPUT_APPEND)
    add_video(INPUT_FILE, OUTPUT_FILE, TEMP_DIR)
elif len(INPUT_FILES_NAMES) > 0:
    # Foldermode
    secure_path(OUTPUT_DIR)
    for input_filename in INPUT_FILES_NAMES:
        filename = extract_filename(input_filename)
        output_filename = customize_filename(input_filename, OUTPUT_APPEND)
        add_video(INPUT_DIR+input_filename, OUTPUT_DIR+output_filename, TEMP_DIR[:-1]+"-"+filename+"/")

print(f"{len(video_arr)} tasks created:\n")

for vid in video_arr:
    vid.work()



Tnow = time.time() - t
print(f"\nFinished in {round(Tnow, 2)} seconds")
