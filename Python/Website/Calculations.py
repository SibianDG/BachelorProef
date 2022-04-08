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

r = sr.Recognizer()

geen_verkleinwoorden = []
with open('geen_verkleinwoorden.txt', 'r') as f:
    geen_verkleinwoorden = f.read().splitlines()

nietzeggendewoorden = []
with open('nietszeggendewoorden.txt', 'r') as f:
    nietzeggendewoorden = f.read().splitlines()


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


def verkleinwoorden(text):
    verkleinwoorden_array = []
    words = make_array_words(text)
    for word in words:
        if word is not None:
            if (len(word) > 3 and word not in geen_verkleinwoorden) and (
                    word.endswith('je') or word.endswith('ke') or word.endswith('kes') or word.endswith('jes')):
                verkleinwoorden_array.append(word)
    if len(verkleinwoorden_array) == 0:
        return '<span class="text-muted">Er zijn geen verkleinwoorden gevonden</span>'
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
        return '<span class="text-muted">Er zijn geen herhalingen gevonden</span>'
    return highlight_words_in_text(text, set(repetition))


def calculate_pitch(wav_file):
    try:
        chunk = 16384
        wf = wave.open(wav_file, 'rb')
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
        return f"Average: {round(freqlistavg, 2)} Hz."
    except Exception as error:
        error_message = f'Fout bij het berekenen van de toonhoogte: {error}.'
        print(error_message)
        return error_message


def make_array_words(text):
    text = re.sub(r'\s{2,}', '', text.lower())
    text = re.sub(r'[^\w\s]', '', text)
    words = text.split()
    return words


def highlight_words_in_text(text: str, words: set):
    for word in words:
        text = text.replace(f'{word}', f'<span class="text-danger">{word}</span>')
    return text
