import soundfile
data, samplerate = soundfile.read('./uploads/20220403160817.wav')
soundfile.write('./uploads/new.wav', data, samplerate, subtype='PCM_16')