from pydub import silence
from moviepy.editor import *
import os
from pydub import AudioSegment


def sidetask(dict):
    # -------------------------------------------------- setup and extrecting audio file_name, process_nr, keep_silence, dcb_offset, silent_length
    file_name, process_nr, keep_silence, dcb_offset, silent_length,return_time_saved = dict
    sys.setrecursionlimit(15000)
    main_clip = VideoFileClip(file_name)

    dotIndex = file_name.rfind(".")
    output_audio_name = file_name[:dotIndex]+".mp3"

    main_audio = main_clip.audio
    main_audio.write_audiofile(filename=output_audio_name,
                               bitrate='30k')
    # ---------------------------------------------------extracts audio
    starting_length = main_clip.duration
    Pure_audio = AudioSegment.from_mp3(output_audio_name)
    dbc = Pure_audio.dBFS
    # --------------------------------------------------- silence_detection
    print("Detecting silence")
    arr_silence = silence.detect_silence(audio_segment=Pure_audio, silence_thresh=dbc - dcb_offset,
                                         min_silence_len=silent_length,
                                         seek_step=5)  # todo seek step value as parameter
    print(f"{len(arr_silence)} silent places detected")
    offset = 0.0
    to_cut = len(arr_silence)
    # ---------------------------------------------------- cutting_part
    for x in range(to_cut - 1):
        main_clip = main_clip.cutout(
            arr_silence[x][0] / 1000 - offset + keep_silence, arr_silence[x][1] / 1000 - offset - keep_silence)
        offset += ((arr_silence[x][1] - arr_silence[x]
                    [0]) / 1000) - 2*keep_silence
        print(f"{x}")

    time_saved = starting_length - main_clip.duration

    print(f"before:{int(starting_length)}  after:{int(main_clip.duration)}  "
          f"seconds saved:{int(time_saved)}")
    main_clip.write_videofile(filename=file_name)

    os.remove(output_audio_name)
    print("{processs_nr} Finished")
    return_time_saved.value = time_saved
    exit(0)
