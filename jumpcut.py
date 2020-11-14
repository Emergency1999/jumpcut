import argparse

import os
import time
import shutil

from silencer import *

def deletePath(s):
    try:  
        shutil.rmtree(s,ignore_errors=False)
    except OSError:  
        print ("Deletion of the directory %s failed" % s)
        print(OSError)

def createPath(s):
    if os.path.exists(s):
        deletePath(s)
    try:  
        os.mkdir(s)
    except OSError:  
        assert False, "Creation of the directory %s failed. (The TEMP folder may already exist. Delete or rename it, and try again.)"



# -------------------------------------------------- ARGS

parser = argparse.ArgumentParser(description="Modifies a video file to cut out silence.")
parser.add_argument("-i", "--input_file",       type = str,                      help = "the video file you want modified")
parser.add_argument("-o", "--output_file",      type = str,                      help = "the output file")
parser.add_argument("-t", "--temp_path",        type = str,     default="TEMP/", help = "the temp directory")
parser.add_argument("-d", "--dcb_threshold",    type = int,     default=10,      help = "the threshold accepted as \"silence\" in dcb")
parser.add_argument("-k", "--keep_silence",     type = float,   default=0.2,     help = "amount of distance from silence to audio in s")
parser.add_argument("-l", "--silent_length",    type = int,     default=500,     help = "the miminum amount of silence in ms")
parser.add_argument("-s", "--seek_step",        type = int,     default=10,      help = "the audio step size in ms")
parser.add_argument("--debug_file",             type = str,     default="",      help = "outputs debug information into file")

args = parser.parse_args()

TEMP_PATH =  args.temp_path
INPUT_FILE = args.input_file
OUTPUT_FILE = args.output_file
DCB_THRESHOLD = args.dcb_threshold
KEEP_SILENCE = args.keep_silence
SILENT_LENGTH = args.silent_length
SEEK_STEP = args.seek_step
DEBUG_FILE = args.debug_file

assert INPUT_FILE is not None, "why u put no input file, that dum"
if OUTPUT_FILE is None:
    dotIndex = INPUT_FILE.rfind(".")
    OUTPUT_FILE = INPUT_FILE[:dotIndex]+"_ALTERED"+INPUT_FILE[dotIndex:]
    i = 0
    while os.path.exists(OUTPUT_FILE):
        OUTPUT_FILE = INPUT_FILE[:dotIndex]+"_ALTERED_"+str(i)+INPUT_FILE[dotIndex:]
        i+=1

t = time.time()
# -------------------------------------------------- CREATE TEMP FOLDER

createPath(TEMP_PATH)
video_length = get_video_length(INPUT_FILE)
print(f"    cutting Video of length {video_length}")

# -------------------------------------------------- EXTRACT AUDIO

ffmpeg_get_audio(INPUT_FILE, TEMP_PATH + "audio.wav")

# -------------------------------------------------- FIND SILENCE

arr_silence_ms = silencer(TEMP_PATH + "audio.wav", DCB_THRESHOLD, SILENT_LENGTH, SEEK_STEP)
print(f"\n    detectet {len(arr_silence_ms)} silences\n")

# -------------------------------------------------- CREATE AUDIO ARRAY

arr_silence_ms.append((video_length, video_length))
arr_audio_s = []
last = 0.0
for x, y in arr_silence_ms:
    start = last
    end = x/1000
    if end-start > 0.01:
        start = max(start-KEEP_SILENCE, 0)
        end = min(end+KEEP_SILENCE, video_length)
        arr_audio_s.append((round(start, 3), round(end, 3)))
    last = y/1000

print(f"\n    created  {len(arr_audio_s)} parts\n")

# -------------------------------------------------- CUT CHUNKS FROM ORIGINAL

print(f"\n    cutting...\n")

ffmpeg_cut_array(INPUT_FILE, OUTPUT_FILE, TEMP_PATH + "script.txt",  arr_audio_s)

# -------------------------------------------------- DELETE TEMP FOLDER

print(f"\n    deleting temp files...\n")
#! deletePath(TEMP_PATH)

# -------------------------------------------------- FINISHED
    
Tnow = time.time()-t
print("\nfinished in %f seconds" % (Tnow))

# debug file
if DEBUG_FILE:
    f = open(DEBUG_FILE, "a")
    f.write(f"{round(video_length/Tnow, 2):5.5}x speed: {round(Tnow, 2):8}s needed for {round(video_length, 2):8}s file: {INPUT_FILE}\n")
    f.close()
