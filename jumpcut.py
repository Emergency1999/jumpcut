
import argparse
from moviepy.editor import *

if __name__ == '__main__':
    # -------------------------------------------------- ARGS
    parser = argparse.ArgumentParser(
        description='Modifies a video file to cut out silence.')
    parser.add_argument('-i', '--input_file', type=str,
                        help='the video file you want modified')
    parser.add_argument('--output_file', type=str,  help="the output file")
    parser.add_argument('--dcb_threshold', type=int, default=10,
                        help="the threshold accepted as \"silence\" in dcb")
    parser.add_argument('--keep_silence', type=float, default=0.2,
                        help="amount of distance from silence to audio in s")
    parser.add_argument('--silent_length', type=int, default=500,
                        help="the miminum amount of silence in ms")

    args = parser.parse_args()

    INPUT_FILE = args.input_file
    OUTPUT_FILE = args.output_file
    DCB_THRESHOLD = args.dcb_threshold
    KEEP_SILENCE = args.keep_silence
    SILENT_LENGTH = args.silent_length

    assert INPUT_FILE is not None, "why u put no input file, that dum"
    if OUTPUT_FILE is None:
        def inputToOutputFilename(filename):
            dotIndex = filename.rfind(".")
            return filename[:dotIndex]+"_ALTERED"+filename[dotIndex:]
        OUTPUT_FILE = inputToOutputFilename(INPUT_FILE)

    # -------------------------------------------------- CUT

    print("initializing...")

    # get length in seconds (float)
    main_clip = VideoFileClip(INPUT_FILE)
    length = main_clip.duration
    main_clip.close()

    print(length)
    # -------------------------------------------------- MULTI

    # -------------------------------------------------- COMBINE
