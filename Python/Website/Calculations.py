import math
import os
import re
from collections import Counter

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

    DIR = './uploads/chunks/'

    numberOfItems = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])

    total_text = ""
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


def verkleinwoorden(text):
    verkleinwoorden_array = []
    words = make_array_words(text)
    for word in words:
        if word is not None:
            if (len(word) > 3 and word not in geen_verkleinwoorden) and (word.endswith('je') or word.endswith('ke') or word.endswith('kes') or word.endswith('jes')) :
                verkleinwoorden_array.append(word)
    return verkleinwoorden_array


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

    return repetition


def make_array_words(text):
    text = re.sub(r'\s{2,}', '', text.lower())
    text = re.sub(r'[^\w\s]', '', text)
    words = text.split()
    return words