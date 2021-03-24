from multiprocessing import Process, Value, Array
from pydub import silence
from pydub import AudioSegment
from moviepy.editor import *
from ownffmpeg import *
import shutil
import time
import math
import sys

# -------------------------------------------------- FUNCTIONS
_max_str_len = 0

def print_manual_reset():
    global _max_str_len
    _max_str_len = 0

def print_manual(s):
    global _max_str_len
    _max_str_len = max(len(s), _max_str_len)
    sys.stdout.write(" "+s.ljust(_max_str_len)+"\r")
    sys.stdout.flush()

def progress_reset():
    print_manual_reset() 

def progress(count, total, status='', bar_len=50):
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    print_manual('[%s] %s%s : %s' % (bar, percents, '%', status))

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

# -------------------------------------------------- Chunkcutter

def Chunkcutter(file_in, file_out, file_audio_comp, file_audio_norm, file_script, dcb_threshold, keep_silence, silent_length, seek_step, return_progress, return_seconds_saved):
    file_in_len = get_video_length(file_in)
    
    # ------------------------------------------------------------ e : extract audio
    ffmpeg_get_audio_comp_norm(file_in, file_audio_comp, file_audio_norm)
    return_progress.value = 0.02
    # ------------------------------------------------------------ d : detect silence
    arr_silence_ms = silence_finder(file_audio_norm, dcb_threshold, silent_length, seek_step)
    arr_silence_ms.append([file_in_len*1000, file_in_len*1000])

    return_progress.value = 0.15
    # ------------------------------------------------------------ --: change array
    arr_audio_s = []
    last = 0.0
    for x, y in arr_silence_ms:
        start = last
        end = x / 1000
        if end - start > 0.01:
            start = max(start - keep_silence, 0)
            end = min(end + keep_silence, file_in_len)
            
            arr_audio_s.append((round(start, 3), round(end, 3)))
        last = y / 1000

    # ------------------------------------------------------------ c : cut chunk
    file_out_len = ffmpeg_cut_array(    videofile_input=file_in,
                                        audiofile_input=file_audio_norm,
                                        file_output=file_out, 
                                        temp_file=file_script, 
                                        timearray=arr_audio_s)
    seconds_saved = file_in_len-file_out_len
    return_seconds_saved.value = seconds_saved
    return_progress.value = 1


# -------------------------------------------------- Videocutter

class Videocutter:
    def __init__(self, input_file, output_file, temp_folder, dcb_threshold, keep_silence, silent_length, seek_step, parallel_max, chunksize, debug_mode):
        self.input_file = input_file
        self.output_file = output_file
        self.temp_folder = temp_folder
        
        self.dcb_threshold = dcb_threshold
        self.keep_silence = keep_silence
        self.silent_length = silent_length
        self.seek_step = seek_step
        self.debug_mode = debug_mode
        self.parallel_max = parallel_max
        self.chunksize = chunksize
        self.video_length = get_video_length(input_file)
        
        create_clear_path(temp_folder)
        # arr_silence_ms = []
        # arr_audio_s = []

        self.all_timer = None
        self.timers = []
        self.timer_name = None
        self.timer = None
        self.prog_max = 1
        self.prog_val = 0

    def __del__(self):
        # deleting Temp folder
        if not self.debug_mode:
            delete_path(self.temp_folder)

    def __new_part_print__(self, print_str, timer_name):
        progress(self.prog_val, self.prog_max, status=print_str)
        self.start_timer(timer_name)

    def work(self):
        progress_reset()
        print(f"TASK {extract_filename(self.input_file)}")
        self.all_timer = time.time()

        parts = math.ceil(self.video_length/(self.chunksize))
        partlen = math.ceil(self.video_length/parts)
        self.prog_max = parts
        # ------------------------------------------------------------ cr: create chunks
        self.__new_part_print__(f"creating {parts} chunks...", "cc")
        
        ffmpeg_segments(file_input=self.input_file,
                        file_output=self.temp_folder + "prechunk%d.mp4",
                        segment_seconds=partlen)

        # ------------------------------------------------------------ --: FOR (parts)
        self.__new_part_print__(f"creating {parts} workers...", "cw")
        workers = []
        work_progress = []
        seconds_saved = []
        seconds_saved_all = 0
        for parti in range(parts):
            part_timer = time.time()
            # print(f"\tchunk {parti+1}/{parts}")
            file_in = self.temp_folder + f"prechunk{parti}.mp4"
            file_out = self.temp_folder + f"chunk{parti}.mp4"
            file_audio_comp = self.temp_folder + f"audio{parti}_comp.wav"
            file_audio_norm = self.temp_folder + f"audio{parti}_norm.wav"
            file_script = self.temp_folder + f"script{parti}.txt"

            return_progress = Value('d', 0.0)
            work_progress.append(return_progress)
            val = Value('d', 0.0)
            seconds_saved.append(val)
            workers.append(Process(target=Chunkcutter, args=(file_in, file_out, file_audio_comp, file_audio_norm, file_script, self.dcb_threshold, self.keep_silence, self.silent_length, self.seek_step, return_progress, val)))

        unstarted = workers.copy()
        # debuginfo = []
        # debugtimer = time.time()
        while True:
            running = list(filter(lambda w: w.is_alive(), workers))

            if len(running) < self.parallel_max and len(unstarted)>0:
                running.append(unstarted.pop())
                running[-1].start()
                time.sleep(0.15)
            
            prog = 0
            for w in work_progress:
                prog += w.value
            self.prog_val = prog

            # debuginfo.append((time.time()-debugtimer, self.prog_val / self.prog_max))
            progress(self.prog_val, self.prog_max, status=f'{len(running)} jobs running, {len(unstarted):2} left')
            if len(unstarted)+len(running) == 0:
                break
            time.sleep(0.1)

        # debugf = open("./text.txt", "a")
        # debugf.write(f"\n{self.input_file}\n")
        # for t, p in debuginfo:
        #     debugf.write(f"{t}\t{p}\n")
        # debugf.close()

        for w in workers:
            w.join()

        for s in seconds_saved:
            seconds_saved_all += s.value

        # ------------------------------------------------------------ co: combine chunks
        self.__new_part_print__(f"combining {parts} chunks...", "co")
        f = open(self.temp_folder + "list.txt", 'w')
        for parti in range(parts):
            file_out = f"chunk{parti}.mp4"
            f.write(f"file '{file_out}'\n")
        f.close()
        ffmpeg_combine(self.temp_folder + "list.txt", self.output_file)

        # ------------------------------------------------------------ --: end
        self.end_timer()
        self.debugger()
        tges = time.time() - self.all_timer
        progress(self.prog_max, self.prog_max, status="done")
        print(f"\nTASK {extract_filename(self.input_file)} done in {round(tges,1)}s ({round(self.video_length/tges,1)}x), {seconds_saved_all:.1f}s {seconds_saved_all/self.video_length*100:2.1f}% removed\n")


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


            tges = time.time() - self.all_timer
            f = open(self.debug_mode, 'a')
            f.write(f"{round(self.video_length / tges, 2):5.2f}x speed: {round(tges, 2):8.2f}s needed for {round(self.video_length, 2):8.2f}s file: {self.input_file}\n")
            f.write(f"{string}\n")
            f.write(f"\n")
            f.close()
