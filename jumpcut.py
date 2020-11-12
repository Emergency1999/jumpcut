import time
import math
import sys
import argparse
import subprocess
from moviepy.editor import *
from multiprocessing import Process, Manager, Value

from tasker import sidetask
# def sidetask(filename, process_nr, keep_silence, dcb_offset, silent_length, return_time_saved):
#     return_time_saved.value = process_nr
#     return

if __name__ == "__main__":
    sys.setrecursionlimit(15000)
    # -------------------------------------------------- ARGS
    parser = argparse.ArgumentParser(
        description="Modifies a video file to cut out silence.")
    parser.add_argument("-i", "--input_file", type=str,
                        help="the video file you want modified")
    parser.add_argument("-o", "--output_file", type=str,  help="the output file")
    parser.add_argument("-t", "--dcb_threshold", type=int, default=10,
                        help="the threshold accepted as \"silence\" in dcb")
    parser.add_argument("-k", "--keep_silence", type=float, default=0.2,
                        help="amount of distance from silence to audio in s")
    parser.add_argument("-l", "--silent_length", type=int, default=500,
                        help="the miminum amount of silence in ms")

    args = parser.parse_args()

    INPUT_FILE = args.input_file
    OUTPUT_FILE = args.output_file
    DCB_THRESHOLD = args.dcb_threshold
    KEEP_SILENCE = args.keep_silence
    SILENT_LENGTH = args.silent_length
    PROCESS_COUNT = 2

    assert INPUT_FILE is not None, "why u put no input file, that dum"
    if OUTPUT_FILE is None:
        dotIndex = INPUT_FILE.rfind(".")
        OUTPUT_FILE = INPUT_FILE[:dotIndex]+"_ALTERED"+INPUT_FILE[dotIndex:]

    # -------------------------------------------------- CUT
    t = time.time()
    print("initializing...")

    # get length in seconds (float)
    main_clip = VideoFileClip(INPUT_FILE)
    length = main_clip.duration
    main_clip.close()

    print("video lenth: " + str(length) + "s")
    seconds = math.ceil(length / PROCESS_COUNT)
    print("cutting video to " + str(PROCESS_COUNT) + " " + str(seconds) + "s chunks...\n\n")

    command = "ffmpeg -i " + INPUT_FILE + \
        " -c copy -map 0 -segment_time " + str(seconds) + \
        " -f segment chunk%d.mp4"
    subprocess.call(command, shell=True)

    print("\n\ncreated ")
    # -------------------------------------------------- PROCESSES
    manager = Manager()
    return_array = [Value('i', 0) for i in range(PROCESS_COUNT)]

    print("creating subprocesses...")

    processes = [Process(target=sidetask, \
        args = ("chunk%d.mp4"%i, i, \
                KEEP_SILENCE, DCB_THRESHOLD, \
                SILENT_LENGTH , return_array[i], \
                )) for i in range(PROCESS_COUNT)]
    

    print("starting subprocesses...")
    for i in range(PROCESS_COUNT):
        processes[i].start()
        processes[i].join()

    

    print("running  subprocesses...")
    for i in range(PROCESS_COUNT):
        processes[i].join()
        print("process %i saved %d seconds" % (i, return_array[i].value))


    # -------------------------------------------------- COMBINE


    Tnow = time.time()-t
    print("\nfinished in %f seconds" % (Tnow))