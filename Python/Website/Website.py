from flask import Flask, render_template, url_for, request, redirect, jsonify
import os
from datetime import datetime
import Calculations
from Calculations import remove_uploads
import shutil

app = Flask(__name__)
app.config['UPLOAD_EXTENSIONS'] = ['.wav', '.mp3']


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        print("POST")
    else:
        return render_template('index.html')


@app.route('/detector', methods=['POST', 'GET'])
def detector():
    if request.method == 'POST':
        print("POST")
    else:
        return render_template('detector.html')


@app.route('/picture_old_woman', methods=['GET'])
def picture_old_woman():
    url = url_for('static', filename='img/rusthuis.jpg')
    print(url)
    return url


@app.route('/privacy', methods=['GET'])
def privacy():
    return render_template('privacy.html')


@app.route('/elderspeak', methods=['GET'])
def elderspeak():
    return render_template('elderspeak.html')


@app.route('/receive_elderspeak', methods=['POST'])
def receive_elderspeak():
    now = datetime.now()
    d1 = now.strftime("%Y%m%d%H%M%S")
    data = request.files['audio_data'].read()
    extra_data = request.form.get('extra_data', "0,0")
    extra_data = extra_data.split(',')
    extra_data = list(map(float, extra_data))
    pitch_normal, loudness_normal = extra_data
    file = f'./uploads/{d1}.wav'

    response_data = {"Hello": "World"}
    with open(os.path.abspath(file), 'wb') as f:
        f.write(data)

    total_text = Calculations.speech_recognition(file)
    total_text = Calculations.replace_hey(total_text)
    verkleinwoorden = Calculations.verkleinwoorden(total_text)
    herhalingen = Calculations.herhalende_zinnen(total_text)
    pitch = Calculations.make_text_compare(pitch_normal,
                                           Calculations.calculate_pitch(Calculations.maketempfile_wav(file)),
                                           40,
                                           '<span class="text-danger">Hoger</span>',
                                           '<span class="text-success">Lager of niet significant hoger.</span>')
    loudness = Calculations.make_text_compare(pitch_normal,
                                              Calculations.loudness(Calculations.maketempfile_wav(file)),
                                              7,
                                              '<span class="text-danger">Luider</span>',
                                              '<span class="text-success">Stiller of niet significant luider.</span>')
    collectieve_voornaamwoorden = Calculations.collectieve_voornaamwoorden(total_text)
    tussenwerpsels = Calculations.tussenwerpsels(total_text)

    response_data["speech_recognition"] = total_text
    response_data["verkleinwoorden"] = verkleinwoorden
    response_data["herhalingen"] = herhalingen
    response_data["pitch"] = pitch
    response_data["loudness"] = loudness
    response_data["collectieve_voornaamwoorden"] = collectieve_voornaamwoorden
    response_data["tussenwerpsels"] = tussenwerpsels

    # return render_template('results.html', text=total_text)
    # laatste stap!

    shutil.rmtree('./uploads/chunks')
    if os.path.exists(file):
        os.remove(file)

    try:
        remove_uploads()
    except Exception as e:
        print(f"Fout bij het verwijderen van de tempfiles: {e}")

    response = jsonify(response_data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    # remove_uploads()
    return response


@app.route('/receive_normal', methods=['POST'])
def receive_normal():
    now = datetime.now()
    d1 = now.strftime("%Y%m%d%H%M%S")
    file = f'./uploads/{d1}.wav'
    data = request.files['audio_data'].read()

    response_data = {"Hello": "World"}
    with open(os.path.abspath(file), 'wb') as f:
        f.write(data)

    print("PITCH BEREKENEN")
    pitch = Calculations.calculate_pitch(Calculations.maketempfile_wav(file))
    loudness = Calculations.loudness(Calculations.maketempfile_wav(file))

    response_data["pitch"] = pitch
    response_data["loudness"] = loudness

    if os.path.exists(file):
        os.remove(file)

    print(response_data)
    response = jsonify(response_data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    # remove_uploads()
    return response


if __name__ == "__main__":
    try:
        app.run(debug=False, host='0.0.0.0')
    finally:
        remove_uploads()
