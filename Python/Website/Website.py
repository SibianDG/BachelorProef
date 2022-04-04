from flask import Flask, render_template, url_for, request, redirect, jsonify
import os
from datetime import datetime
import Calculations
app = Flask(__name__)
app.config['UPLOAD_EXTENSIONS'] = ['.wav']


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        print("POST")
    else:
        return render_template('index.html')


@app.route('/privacy', methods=['GET'])
def privacy():
    return render_template('privacy.html')


@app.route('/elderspeak', methods=['GET'])
def elderspeak():
    return render_template('elderspeak.html')


# https://stackoverflow.com/questions/70733510/send-blob-to-python-flask-and-then-save-it
@app.route('/receive', methods=['POST'])
def receive():
    now = datetime.now()
    d1 = now.strftime("%Y%m%d%H%M%S")
    data = request.files['audio_data'].read()
    file = f'./uploads/{d1}.wav'

    response_data = {"test": "Hello?"}
    with open(os.path.abspath(file), 'wb') as f:
        f.write(data)
    try:
        total_text = Calculations.speech_recognition(file)
    except:
        total_text = "ERROR"
    response_data["speech_recognition"] = total_text

    response = jsonify(response_data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


    #return render_template('results.html', text=total_text)
    # laatste stap!
    # if os.path.exists('./uploads/chunks'):
    #    os.rmdir('./uploads/chunks')
    #    if os.path.exists(file):
#        os.remove(file)


if __name__ == "__main__":
    app.run(debug=True)
