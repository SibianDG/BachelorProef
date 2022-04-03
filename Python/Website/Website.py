import math

from flask import Flask, render_template, url_for, request, redirect, jsonify
# from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json
import speech_recognition as sr
from datetime import datetime
from pydub import AudioSegment
# from pydub.utils import mediainfo
from pydub.utils import make_chunks, which

app = Flask(__name__)
app.config['UPLOAD_EXTENSIONS'] = ['.wav']
r = sr.Recognizer()

def to_chuncks(file):
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

    file_split_size = 20000000  # 10Mb OR 10, 000, 000 bytes
    total_chunks = wav_file_size // file_split_size

    # Get chunk size by following method #There are more than one ofcourse
    # for  duration_in_sec (X) -->  wav_file_size (Y)
    # So   whats duration in sec  (K) --> for file size of 10Mb
    #  K = X * 10Mb / Y

    chunk_length_in_sec = math.ceil((duration_in_sec * 10000000) / wav_file_size)  # in sec
    chunk_length_ms = chunk_length_in_sec * 1000
    chunks = make_chunks(myaudio, chunk_length_ms)

    # Export all of the individual chunks as wav files

    if not os.path.exists('./uploads/chunks'):
        os.makedirs('./uploads/chunks')

    for i, chunk in enumerate(chunks):
        chunk_name = f"./uploads/chunks/chunck{i}.flac"
        print("exporting", chunk_name)
        chunk.export(chunk_name, format="flac")


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        # new_task = Todo(content=task_content)

        # try:
        #     # db.session.add(new_task)
        #     db.session.commit()
        #     return redirect('/')
        # except:
        #     return 'There was an issue adding your task'

    else:
        return render_template('index.html')


# https://stackoverflow.com/questions/70733510/send-blob-to-python-flask-and-then-save-it
@app.route('/receive', methods=['POST'])
def receive():
    now = datetime.now()
    d1 = now.strftime("%Y%m%d%H%M%S")

    # TODO: eerst in chuncks
    data = request.files['audio_data'].read()

    file = f'./uploads/{d1}.wav'
    with open(os.path.abspath(file), 'wb') as f:
        f.write(data)
    to_chuncks(file)
    audio_file = sr.AudioFile('./uploads/chunks/chunck0.flac')
    with audio_file as source:
        r.adjust_for_ambient_noise(source)
        audio = r.record(source)
        text = r.recognize_google(audio_data=audio, language="nl-BE")
        print("######## Google Recognize ####################")
        print(text)
        print("##############################################")
    response = jsonify(text)
    response.headers.add('Access-Control-Allow-Origin', '*')

    # laatste stap!
    #if os.path.exists('./uploads/chunks'):
    #    os.rmdir('./uploads/chunks')
    #    if os.path.exists(file):
#        os.remove(file)
    return response


if __name__ == "__main__":
    app.run(debug=True)
