

def sidetask(i, keep_silence, dcb_offset, silent_length):
    # initial_setup
    sys.setrecursionlimit(15000)
    main_clip = VideoFileClip(i  # !)

    main_audio=main_clip.audio
    main_audio.write_audiofile(filename='PureAudio.mp3',
                               bitrate='30k')  # extracts audio
    starting_length=main_clip.duration
    Pure_audio=AudioSegment.from_mp3('PureAudio.mp3')
    dbc=Pure_audio.dBFS
    # silence_detection
    print("Detecting silence")
    arr_silence=silence.detect_silence(audio_segment=Pure_audio, silence_thresh=dbc - dcb_offset,
                                         min_silence_len=silent_length,
                                         seek_step=5)
    print(f"{len(arr_silence)} silent places detected")
    offset=0.0
    to_cut=len(arr_silence)
    # cutting part
    for x in range(to_cut - 1):
        main_clip=main_clip.cutout(
            arr_silence[x][0] / 1000 - offset + keep_silence, arr_silence[x][1] / 1000 - offset - keep_silence)
        offset += ((arr_silence[x][1] - arr_silence[x]
                    [0]) / 1000) - 2*keep_silence
        print(f"{x}")

    print(f"before:{int(starting_length)}  after:{int(main_clip.duration)}  "
          f"seconds saved:{int(starting_length - main_clip.duration)}")
    main_clip.write_videofile(filename=sys.argv[2]  # !)

    os.remove('PureAudio.mp3')
    print("Finished")