from pydub import silence
from pydub import AudioSegment
from moviepy.editor import *
from ownffmpeg import *
import shutil
import time
import math

# -------------------------------------------------- FUNCTIONS

# ------------------------- file/directory

def delete_path(s):
    try:
        shutil.rmtree(s, ignore_errors=False)
    except OSError:
        print(f"Deletion of the directory {s} failed")
        print(OSError)
def delete_path_try(s):
    if os.path.exists(s):
        delete_path(s)

def create_path(s):
    try:
        os.mkdir(s)
    except OSError:
        assert False, f"Creation of the directory {s} failed. (The TEMP folder may already exist. Delete or rename it, and try again.)"

def create_clear_path(s):
    if os.path.exists(s):
        delete_path(s)
    create_path(s)

def secure_path(s):
    if not os.path.exists(s):
        create_path(s)


def output_name(name):
    dot_index = name.rfind(".")
    return name[:dot_index] + "_ALTERED" + name[dot_index:]

def extract_filename(path):
    return os.path.splitext(os.path.basename(path))[0]

def customize_filename(path, appendstr):
    a, b = os.path.splitext(path)
    return a + appendstr + b

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

# -------------------------------------------------- Videocutter

class Videocutter:
    def __init__(self, input_file, output_file, temp_folder, dcb_threshold, keep_silence, silent_length, seek_step, chunksize, debug_mode):
        self.input_file = input_file
        self.output_file = output_file
        self.temp_folder = temp_folder
        
        self.dcb_threshold = dcb_threshold
        self.keep_silence = keep_silence
        self.silent_length = silent_length
        self.seek_step = seek_step
        self.debug_mode = debug_mode
        self.chunksize = chunksize
        self.video_length = get_video_length(input_file)
        
        create_clear_path(temp_folder)
        self.arr_silence_ms = []
        self.arr_audio_s = []

        self.all_timer = None
        self.timers = []
        self.timer_name = None
        self.timer = None

    def __del__(self):
        # deleting Temp folder
        if not self.debug_mode:
            delete_path(self.temp_folder)

    def extract_audio(self):
        ffmpeg_get_audio(self.input_file, self.temp_folder + "audio.wav")

    def detect_silence(self):
        self.arr_silence_ms = silence_finder(self.temp_folder + "audio.wav", self.dcb_threshold, self.silent_length, self.seek_step)
        self.arr_silence_ms.append((self.video_length, self.video_length))

    def create_arr_audio_s(self):
        last = 0.0
        for x, y in self.arr_silence_ms:
            start = last
            end = x / 1000
            if end - start > 0.01:
                start = max(start - self.keep_silence, 0)
                end = min(end + self.keep_silence, self.video_length)
                self.arr_audio_s.append((round(start, 3), round(end, 3)))
            last = y / 1000

    def cut_chunk(self, chunk, nr):
        ffmpeg_cut_array(file_input=self.input_file,
                         file_output=self.temp_folder + f"chunk{nr}.mp4", 
                         temp_file=self.temp_folder + f"script{nr}.txt", 
                         timearray=chunk)

    def cut_array_in_chunks(self):
        chunks = [self.arr_audio_s[i:i + self.chunksize] for i in range(0, len(self.arr_audio_s), self.chunksize)]
        self.chunk_len = 0
        for chunk in chunks:
            self.start_timer(f"chunk_{self.chunk_len+1}")
            print(f"cutting chunk {self.chunk_len+1}...")
            self.cut_chunk(chunk, self.chunk_len)
            self.chunk_len+=1

    def combine_chunks(self):
        f = open(self.temp_folder + "list.txt", 'w')
        for nr in range(self.chunk_len):
            f.write(f"file 'chunk{nr}.mp4'\n")
        f.close()
        ffmpeg_combine(self.temp_folder + "list.txt", self.output_file)

    def work(self):
        print(f"TASK {self.input_file} started")

        print(f"extracting audio...")
        self.all_timer = time.time()
        self.start_timer("extract_audio")
        self.extract_audio()

        print(f"detecting silence...")
        self.start_timer("detect_silence")
        self.detect_silence()

        print(f"{len(self.arr_silence_ms)} silences detected")
        self.create_arr_audio_s()
        self.start_timer("create_array")
        print(f"{len(self.arr_audio_s)} cuts necessary")

        print(f"creating {math.ceil(len(self.arr_audio_s)/self.chunksize)} chunks...")
        self.cut_array_in_chunks()

        print(f"combining {math.ceil(len(self.arr_audio_s)/self.chunksize)} chunks...")
        self.start_timer("combine_chunks")
        self.combine_chunks()

        self.end_timer()
        self.debugger()
        print(f"TASK {self.input_file} done\n")

    def start_timer(self, name):
        self.end_timer()
        self.timer_name = name
        self.timer = time.time()

    def end_timer(self):
        if self.timer_name:
            t_now = time.time() - self.timer
            self.timers.append({"name":self.timer_name, "time":round(t_now, 1)})
            self.timer_name = None



    def debugger(self):
        if self.debug_mode:
            string = ', '.join([f"{t['name']}: {t['time']:4.1f}" for t in self.timers])
            print(f"debuginfo saved")


            tges = time.time() - self.all_timer
            f = open(self.debug_mode, 'a')
            f.write(f"{round(self.video_length / tges, 2):5.2f}x speed: {round(tges, 2):8.2f}s needed for {round(self.video_length, 2):8.2f}s file: {self.input_file}\n")
            f.write(f"{string}\n")
            f.write(f"\n")
            f.close()
