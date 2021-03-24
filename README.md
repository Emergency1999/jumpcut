# HOWTO install

- install ffmpeg
- install sox
- install python3
- install packages pydub moviepy


```
sudo apt-get install ffmpeg sox python3 -y
pip3 install pydub moviepy 

```

# HOWTO useage

python3 jumpcut.py [args]
| ARG | ARGUMENT           | TYPE | DEFAULT   | DESCRIPTION                                                                           |
| --- | ------------------ | ---- | --------- | ------------------------------------------------------------------------------------- |
| -i  | --input_file       | str  |           | the video file you want modified                                                      |
| -o  | --output_file      | str  |           | the output file                                                                       |
| -id | --input_directory  | str  | "INPUT/"  | the input directory                                                                   |
| -od | --output_directory | str  | "OUTPUT/" | the output directory                                                                  |
| -a  | --output_append    | str  | "_cut"    | changes the ending of outputfile if desired, \".\" means none                         |
| -t  | --temp_directory   | str  | "TEMP/"   | the temp directory                                                                    |
| -c  | --check_existing   | bool | False     | checks for every file if the outputfile already exists. If yes, the file will be skip |
|     |                    |      |           |                                                                                       |
| -dt | --dcb_threshold    | int  | 14        | the threshold accepted as \"silence\" in dcb                                          |
| -ks | --keep_silence     | int  | 200       | amount of distance from silence to audio in ms                                        |
| -sl | --silent_length    | int  | 500       | the miminum amount of silence in ms                                                   |
| -ss | --seek_step        | int  | 10         | the audio step size in ms                                                             |
| -cs | --chunksize        | int  | 200       | the videopart chunk size in seconds in which the video is split before cutting        |
| -p  | --parallel_max     | int  | 1         | maximum of parallel running jobs                                                      |
| -dm | --debug_mode       | str  | ""        | enables debug information to file given and stops deletion of temp-files              |
