import math
import os
import re
import wave
from collections import Counter

import numpy as np
import pyaudio
from pydub import AudioSegment
# from pydub.utils import mediainfo
from pydub.utils import make_chunks, which
import speech_recognition as sr

import librosa
import soundfile as sf
import pyloudnorm as pyln

r = sr.Recognizer()

geen_verkleinwoorden = []
with open('geen_verkleinwoorden.txt', 'r') as f:
    geen_verkleinwoorden = f.read().splitlines()

nietzeggendewoorden = []
with open('nietszeggendewoorden.txt', 'r') as f:
    nietzeggendewoorden = f.read().splitlines()

tussenwerpels_woorden = []
with open('tussenwerpsels.txt', 'r') as f:
    tussenwerpels_woorden = f.read().splitlines()


def speech_recognition(file):
    try:

        print(file, ' to chunks')
        AudioSegment.converter = which("ffmpeg")
        myaudio = AudioSegment.from_file(file)
        channel_count = myaudio.channels  # Get channels
        sample_width = myaudio.sample_width  # Get sample width
        duration_in_sec = len(myaudio) / 1000  # Length of audio in sec
        sample_rate = myaudio.frame_rate

        print("sample_width=", sample_width)
        print("channel_count=", channel_count)
        print("duration_in_sec=", duration_in_sec)
        print("frame_rate=", sample_rate)
        bit_rate = 16  # assumption , you can extract from mediainfo("test.wav") dynamically

        wav_file_size = (sample_rate * bit_rate * channel_count * duration_in_sec) / 20
        print("wav_file_size = ", wav_file_size)

        file_split_size = 25000000  # 10Mb OR 10, 000, 000 bytes
        total_chunks = wav_file_size // file_split_size

        # Get chunk size by following method #There are more than one ofcourse
        # for  duration_in_sec (X) -->  wav_file_size (Y)
        # So   whats duration in sec  (K) --> for file size of 10Mb
        #  K = X * 10Mb / Y

        chunk_length_in_sec = math.ceil((duration_in_sec * 20000000) / wav_file_size)  # in sec
        chunk_length_ms = chunk_length_in_sec * 2000
        chunks = make_chunks(myaudio, chunk_length_ms)

        # Export all of the individual chunks as wav files

        if not os.path.exists('./uploads/chunks'):
            os.makedirs('./uploads/chunks')

        for i, chunk in enumerate(chunks):
            chunk_name = f"./uploads/chunks/chunck{i}.flac"
            print("exporting", chunk_name)
            chunk.export(chunk_name, format="flac")
    except Exception as error:
        error_message = f'Fout bij het bewerken van de audiofile: {error}.'
        print(error_message)
        return error_message

    DIR = './uploads/chunks/'

    numberOfItems = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])

    total_text = ""

    try:
        for i in range(numberOfItems):
            # Speech Recognition
            audio_file = sr.AudioFile(f'./uploads/chunks/chunck{i}.flac')
            with audio_file as source:
                r.adjust_for_ambient_noise(source)
                audio = r.record(source)
                text = r.recognize_google(audio_data=audio, language="nl-BE")
                total_text += " " + text
                print("######## Google Recognize ####################")
                print(text)
                print("##############################################")
        return total_text.strip()
    except Exception as error:
        error_message = f'Fout bij de spraakherkenning: {error}.'
        print(error_message)
        return error_message


def collectieve_voornaamwoorden(text):
    collectieve_voornaamwoorden_array = []
    words = make_array_words(text)
    for word in words:
        if word is not None and word == "we":  # TODO uitbreiden?
            collectieve_voornaamwoorden_array.append(word)
    c = dict(Counter(collectieve_voornaamwoorden_array))
    filtered_dict = {k: v for (k, v) in c.items() if v > 1}
    l = list(filtered_dict.keys())
    if len(l) == 0:
        return '<span class="text-success">Er werden geen of niet genoeg collectieve voornaamwoorden gebruikt.</span>'
    return highlight_words_in_text(text, set(l))


def tussenwerpsels(text):
    tussenwerpsels_array = []
    words = make_array_words(text)
    for word in words:
        if word is not None and word in tussenwerpels_woorden:  # TODO uitbreiden?
            tussenwerpsels_array.append(word)
    c = dict(Counter(tussenwerpsels_array))
    filtered_dict = {k: v for (k, v) in c.items() if v > 1}
    l = list(filtered_dict.keys())
    if len(l) == 0:
        return '<span class="text-success">Er werden geen of niet genoeg tussenwerpsels gebruikt.</span>'
    return highlight_words_in_text(text, set(l))


def verkleinwoorden(text):
    verkleinwoorden_array = []
    words = make_array_words(text)
    for word in words:
        if word is not None:
            if (len(word) > 3 and word not in geen_verkleinwoorden) and (
                    word.endswith('je') or word.endswith('ke') or word.endswith('kes') or word.endswith('jes')):
                verkleinwoorden_array.append(word)
    if len(verkleinwoorden_array) == 0:
        return '<span class="text-success">Er zijn geen verkleinwoorden gevonden</span>'
    return highlight_words_in_text(text, set(verkleinwoorden_array))


def herhalende_zinnen(text):
    words = make_array_words(text)

    cache = []
    toBeDeleted = []
    repetition = []

    for word in words:
        if word is not None:
            while len(cache) >= 30:
                cache.pop(0)
            if word not in nietzeggendewoorden:
                cache.append(word)

    sameequals = dict()

    sameequals = {word: cache.count(word) for word in cache}

    if sameequals is not None and len(sameequals) != 0:
        for word in sameequals:
            if sameequals[word] == 1:
                toBeDeleted.append(word)
            else:
                repetition.append(word)
        for word in toBeDeleted:
            del sameequals[word]

    if len(repetition) == 0:
        return '<span class="text-success">Er zijn geen herhalingen gevonden</span>'
    return highlight_words_in_text(text, set(repetition))


def maketempfile_wav(wav_file):
    x, _ = librosa.load(wav_file, sr=16000)
    tmp_file = './uploads/tmp.wav'
    sf.write(tmp_file, x, 16000)
    return tmp_file


def calculate_pitch(wav_file):
    try:
        x, _ = librosa.load(wav_file, sr=16000)
        tmp_file = './uploads/tmp.wav'
        sf.write(tmp_file, x, 16000)

        chunk = 16384
        with wave.open(tmp_file, 'r') as wf:
            swidth = wf.getsampwidth()
            RATE = wf.getframerate()
            window = np.blackman(chunk)
            p = pyaudio.PyAudio()
            stream = p.open(format=
                            p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=RATE,
                            output=True)
            data = wf.readframes(chunk)
            freqlist = []
            while len(data) == chunk * swidth:
                # write data out to the audio stream
                stream.write(data)
                # unpack the data and times by the hamming window
                indata = np.array(wave.struct.unpack("%dh" % (len(data) / swidth),
                                                     data)) * window
                # Take the fft and square each value
                fftData = abs(np.fft.rfft(indata)) ** 2
                # find the maximum
                which = fftData[1:].argmax() + 1
                # use quadratic interpolation around the max
                if which != len(fftData) - 1:
                    y0, y1, y2 = np.log(fftData[which - 1:which + 2:])
                    x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
                    # find the frequency and output it
                    thefreq = (which + x1) * RATE / chunk
                    print("The freq is %.0f Hz." % (thefreq))
                    freqlist.append(thefreq)
                else:
                    thefreq = which * RATE / chunk
                    print("The freq is %.0f Hz." % (thefreq))
                    freqlist.append(thefreq)
                # read some more data
                data = wf.readframes(chunk)
        if data:
            stream.write(data)
        freqlistavg = sum(freqlist) / len(freqlist)
        print("Average: %0.2f Hz." % (freqlistavg))
        stream.close()
        p.terminate()
        return round(freqlistavg, 2)
    except Exception as error:
        error_message = f'Fout bij het berekenen van de toonhoogte: {error}.'
        print(error_message)
        return error_message
    finally:
        if tmp_file is not None and os.path.exists(tmp_file):
            os.remove(tmp_file)


def make_text_compare(normal, current, difference, danger, success):
    if normal is not None and current is not None and normal != 0 and current != 0:
        if normal + difference < current:
            return danger
        return success
    else:
        return '<span class="text-muted">Er was een probleem met deze functie. Probeer opnieuw.</span>'


def loudness(wav):
    data, rate = sf.read(wav)  # load audio (with shape (samples, channels))
    meter = pyln.Meter(rate)  # create BS.1770 meter
    loudness_range = meter.integrated_loudness(data)  # measure loudness
    if float('inf') == loudness_range:
        loudness_range = 10000
    elif float('-inf') == loudness_range:
        loudness_range = -10000
    return loudness_range


def make_array_words(text):
    text = re.sub(r'\s{2,}', '', text.lower())
    text = re.sub(r'[^\w\s]', '', text)
    words = text.split()
    return words


def highlight_words_in_text(text: str, words: set):
    for word in words:
        text = text.replace(f'{word}', f'<span class="text-danger">{word}</span>')
    return text
