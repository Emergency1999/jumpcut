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
        # arr_silence_ms = []
        # arr_audio_s = []

        self.all_timer = None
        self.timers = []
        self.timer_name = None
        self.timer = None

    def __del__(self):
        # deleting Temp folder
        if not self.debug_mode:
            delete_path(self.temp_folder)

    def __new_part_print__(self, print_str, timer_name):
        print(print_str)
        self.start_timer(timer_name)

    def work(self):
        print(f"TASK {self.input_file} started")
        self.all_timer = time.time()

        parts = math.ceil(self.video_length/(5*60))
        partlen = math.ceil(self.video_length/parts)
        # ------------------------------------------------------------ cr: create chunks
        self.__new_part_print__(f"creating {parts} chunks...", "cc")
        
        ffmpeg_segments(file_input=self.input_file,
                        file_output=self.temp_folder + "prechunk%d.mp4",
                        segment_seconds=partlen)

        # ------------------------------------------------------------ --: FOR (parts)
        for parti in range(parts):
            print(f"\nCHUNK {parti}")
            file_in = self.temp_folder + f"prechunk{parti}.mp4"
            file_out = self.temp_folder + f"chunk{parti}.mp4"
            file_audio = self.temp_folder + f"audio{parti}.wav"
            file_script = self.temp_folder + f"script{parti}.txt"
            file_in_len = get_video_length(file_in)

            # ------------------------------------------------------------ e : extract audio
            self.__new_part_print__(f"extracting audio...", f"e{parti}")
            ffmpeg_get_audio(file_in, file_audio)

            # ------------------------------------------------------------ d : detect silence
            self.__new_part_print__(f"detecting silence...", f"d{parti}")
            arr_silence_ms = silence_finder(file_audio, self.dcb_threshold, self.silent_length, self.seek_step)
            arr_silence_ms.append((file_in_len, file_in_len))

            # ------------------------------------------------------------ --: change array
            print(f"{len(arr_silence_ms)} silences detected")
            arr_audio_s = []
            last = 0.0
            for x, y in arr_silence_ms:
                start = last
                end = x / 1000
                if end - start > 0.01:
                    start = max(start - self.keep_silence, 0)
                    end = min(end + self.keep_silence, self.video_length)
                    arr_audio_s.append((round(start, 3), round(end, 3)))
                last = y / 1000

            print(f"{len(arr_audio_s)} cuts necessary")

            # ------------------------------------------------------------ c : cut chunk
            self.__new_part_print__(f"cutting chunk...", f"c{parti}")
            ffmpeg_cut_array(file_input=file_in,
                            file_output=file_out, 
                            temp_file=file_script, 
                            timearray=arr_audio_s)



        # ------------------------------------------------------------ co: combine chunks
        self.__new_part_print__(f"combining {math.ceil(len(arr_audio_s)/self.chunksize)} chunks...", "co")
        f = open(self.temp_folder + "list.txt", 'w')
        for parti in range(parts):
            file_out = f"chunk{parti}.mp4"
            f.write(f"file '{file_out}'\n")
        f.close()
        ffmpeg_combine(self.temp_folder + "list.txt", self.output_file)

        # ------------------------------------------------------------ --: end
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
