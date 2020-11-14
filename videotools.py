from pydub import silence
from pydub import AudioSegment
from moviepy.editor import *
import subprocess
import shutil
import time

# -------------------------------------------------- FUNCTIONS

# ------------------------- file/directory

def delete_path(s):
    try:
        shutil.rmtree(s, ignore_errors=False)
    except OSError:
        print(f"Deletion of the directory {s} failed")
        print(OSError)

def create_path(s):
    try:
        os.mkdir(s)
    except OSError:
        assert False, f"Creation of the directory {s} failed. (The TEMP folder may already exist. Delete or rename it, and try again.)"

def create_clear_path(s):
    if os.path.exists(s):
        deletePath(s)
    createPath(s)

def secure_path(s):
    if not os.path.exists(s):
        createPath(s)


def output_name(name):
    dot_index = name.rfind(".")
    return name[:dot_index] + "_ALTERED" + name[dot_index:]

def extract_filename(path):
    return os.path.splitext(os.path.basename(path))[0]

# ------------------------- video/audio

def silence_finder(audio_wav, dcb_offset=10, silent_length=500,step_in_ms=10):
    Pure_audio = AudioSegment.from_wav(audio_wav)
    dbc = Pure_audio.dBFS
    return silence.detect_silence(audio_segment=Pure_audio, silence_thresh=dbc - dcb_offset, min_silence_len=silent_length, seek_step=step_in_ms)

def get_video_length(file_name):
    clip = VideoFileClip(file_name)
    duration = clip.duration
    clip.close()
    return duration

# -------------------------------------------------- FFMPEG

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

# -------------------------------------------------- Videocutter

class Videocutter:
    def __init__(self, input_file, output_file, temp_folder, dcb_threshold, keep_silence, silent_length, seek_step, debug_mode=False):
        self.input_file = input_file
        self.output_file = output_file
        self.temp_folder = temp_folder

        self.dcb_threshold = dcb_threshold
        self.keep_silence = keep_silence
        self.silent_length = silent_length
        self.seek_step = seek_step
        self.debug_mode = debug_mode
        self.video_length = get_video_length(input_file)
        
        create_clear_path(temp_folder)
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
        if self.debug_mode:
            t_now = time.time() - self.start_time
            print("Output debug information")
            f = open('debug.txt', 'a+')
            f.write(
                f"{round(self.video_length / t_now, 2):5.5}x speed: {round(t_now, 2):8}s needed for {round(self.video_length, 2):8}s file: {self.input_path}{self.input_file}\n")
            f.close()
