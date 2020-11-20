import subprocess

# -------------------------------------------------- FFMPEG

def ffmpeg_get_audio(file_input, file_output):
    command = f"ffmpeg -y -hide_banner -loglevel warning -i \"{file_input}\" -ab 160k -ac 2 -ar 44100 -vn \"{file_output}\""
    subprocess.call(command, shell=True)

def ffmpeg_cut_array(file_input, file_output, temp_file, timearray):
    # create temp file with filter_complex_script
    full_length = 0
    f = open(temp_file, "w")
    i = 0
    for start, end in timearray:
        full_length += end - start
        f.write(f"[0:v]trim=start={str(start)}:end={str(end)},setpts=PTS-STARTPTS[v{i}];")
        f.write(f"[0:a]atrim=start={str(start)}:end={str(end)},asetpts=PTS-STARTPTS[a{i}];")
        i+=1
    length = i
    i = 0
    if length > 1:
        for i in range(length):
            f.write(f"[v{i}][a{i}]")
        f.write(f"concat=n={length}:v=1:a=1[v{length}][a{length}]")
        last = length
    else:
        last = i
    f.close()

    # execute script
    command = f"ffmpeg -y -hide_banner -loglevel warning -i \"{file_input}\" -filter_complex_script \"{temp_file}\" -async 1 -safe 0 -map [v{last}] -map [a{last}] -to {full_length} \"{file_output}\""
    # print(command)
    subprocess.call(command, shell=True)

def ffmpeg_cut(file_input, file_output, start, end, additional_flag=""):
    command = f"ffmpeg -y -hide_banner -loglevel warning -i \"{file_input}\" -ss {str(start)} -to {str(end)} {additional_flag} \"{file_output}\""
    subprocess.call(command, shell=True)

def ffmpeg_combine(file_input, file_output):
    command = f"ffmpeg -y -hide_banner -loglevel warning -f concat -safe 0 -i \"{file_input}\" -c copy \"{file_output}\"" #todo give option to run without -c copy to fully compress (takes longer)
    subprocess.call(command, shell=True)
