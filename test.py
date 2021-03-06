import time
import subprocess

t = time.time()

# command = "ffmpeg -i " + "\"Vorlesung 09.mp4\"" + \
#         " chunkall.mp4"

# command = "ffmpeg -i " + "\"Vorlesung 09.mp4\"" + \
#         " -ab 160k -ac 2 -ar 44100 -vn audio.mp3"

# command = "ffmpeg -i " + "\"video/Vorlesung 09.mp4\"" + \
#         " -ab 160k -ac 2 -ar 44100 -vn audio.wav"

command = "ffmpeg -f concat -safe 0 -i 'list.txt' -c copy '.\video\small_ALTERED.mp4'"
# command = "dir .\TEMP"

# command = "ffmpeg -i " + "\"video/test.mp4\"" + \
#         " -ab 160k -ac 2 -ar 44100 -vn -ss 0 -to 120  audiopart.wav"


subprocess.call(command, shell=True)

Tnow = time.time()-t
print("\nfinished in %f seconds" % (Tnow))