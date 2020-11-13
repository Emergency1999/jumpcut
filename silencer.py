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

def cut_from_original(file_input, file_output, start, end):
    command = "ffmpeg -i " + '"' + file_input + '" -ss ' + str(start) + " -to " + str(end) + ' "' + file_output + '"'
    subprocess.call(command, shell=True)
