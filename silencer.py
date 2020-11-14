from pydub import silence
from pydub import AudioSegment
from moviepy.editor import *
import subprocess


def silencer(audio_wav, dcb_offset=10, silent_length=500,step_in_ms=10):
    Pure_audio = AudioSegment.from_wav(audio_wav)
    dbc = Pure_audio.dBFS
    return silence.detect_silence(audio_segment=Pure_audio, silence_thresh=dbc - dcb_offset, min_silence_len=silent_length, seek_step=step_in_ms)



def get_video_length(file_name):
    clip = VideoFileClip(file_name)
    duration = clip.duration
    clip.close()
    return duration

def ffmpeg_get_audio(file_input, file_output):
    command = f"ffmpeg -i \"{file_input}\" -ab 160k -ac 2 -ar 44100 -vn \"{file_output}\""
    subprocess.call(command, shell=True)


def ffmpeg_cut_array(file_input, file_output, temp_file, timearray):
    # create temp file with filter_complex_script
    f = open(temp_file, "a")
    i = 0
    for start, end in timearray:
        f.write(f"[0:v]trim=start={str(start)}:end={str(end)},setpts=PTS-STARTPTS[vpart{i}];")
        f.write(f"[0:a]atrim=start={str(start)}:end={str(end)},asetpts=PTS-STARTPTS[apart{i}];")
        i+=1
    length = i
    i = 0
    for i in range(length):
        f.write(f"[vpart{i}][apart{i}]")
    f.write(f"concat=n={length}:v=1:a=1[vout][aout]")
    f.close()

    # execute script
    command = f"ffmpeg -i \"{file_input}\" -filter_complex_script \"{temp_file}\" -map [vout] -map [aout] \"{file_output}\""
    # print(command)
    subprocess.call(command, shell=True)


def ffmpeg_cut_from_original(file_input, file_output, start, end):
    command = f"ffmpeg -i \"{file_input}\" -ss {str(start)} -to {str(end)} \"{file_output}\""
    subprocess.call(command, shell=True)

def ffmpeg_combile(file_input, file_output):
    command = f"ffmpeg -f concat -safe 0 -i \"{file_input}\" -c copy \"{file_output}\"" #todo give option to run without -c copy to fully compress (takes longer)
    subprocess.call(command, shell=True)
