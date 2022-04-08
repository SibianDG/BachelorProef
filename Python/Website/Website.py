from flask import Flask, render_template, url_for, request, redirect, jsonify
import os
from datetime import datetime
import Calculations
import shutil

app = Flask(__name__)
app.config['UPLOAD_EXTENSIONS'] = ['.wav']


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        print("POST")
    else:
        return render_template('index.html')


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
    file = f'./uploads/{d1}.wav'

    response_data = {"Hello": "World"}
    with open(os.path.abspath(file), 'wb') as f:
        f.write(data)

    total_text = Calculations.speech_recognition(file)
    verkleinwoorden = Calculations.verkleinwoorden(total_text)
    herhalingen = Calculations.herhalende_zinnen(total_text)
    pitch = Calculations.calculate_pitch(file)

    response_data["speech_recognition"] = total_text
    response_data["verkleinwoorden"] = verkleinwoorden
    response_data["herhalingen"] = herhalingen
    response_data["pitch"] = pitch

    # return render_template('results.html', text=total_text)
    # laatste stap!

    shutil.rmtree('./uploads/chunks')
    if os.path.exists(file):
        os.remove(file)

    response = jsonify(response_data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/receive_normal', methods=['POST'])
def receive_normal():
    now = datetime.now()
    d1 = now.strftime("%Y%m%d%H%M%S")
    data = request.files['audio_data'].read()
    file = f'./uploads/{d1}.wav'

    response_data = {"Hello": "World"}
    with open(os.path.abspath(file), 'wb') as f:
        f.write(data)

    print("PITCH BEREKENEN")
    pitch = Calculations.calculate_pitch(file)

    response_data["pitch"] = pitch

    if os.path.exists(file):
        os.remove(file)

    response = jsonify(response_data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


if __name__ == "__main__":
    app.run(debug=True)
