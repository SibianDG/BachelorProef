from flask import Flask, render_template, url_for, request, redirect, jsonify
# from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json
import speech_recognition as sr

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
# db = SQLAlchemy(app)
r = sr.Recognizer()


def abc():
    print("test")


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
    # TODO: eerst in chuncks
    f = open('./file.wav', 'wb')
    f.write(request.data)
    f.close()
    # audio_input = request.files['file']
    # # file = files.get('file')
    # print("0000000000000000000000000000")
    # print(audio_input)
    audio_file = sr.AudioFile(request.data)
    with audio_file as source:
        audio_file = r.record(source)
        text = r.recognize_google(audio_data=audio_file, language="nl-be")
        print(text)
    return text
    # # with open(os.path.abspath(f'uploads/test.wav'), 'wb') as f:
    # #     f.write(audio_input)
    #
    # response = jsonify("File received and saved!")
    # response.headers.add('Access-Control-Allow-Origin', '*')
    #
    # return response


# @app.route('/delete/<int:id>')
# def delete(id):
#     r = 1
#     # task_to_delete = Todo.query.get_or_404(id)
#
#     # try:
#     #     db.session.delete(task_to_delete)
#     #     db.session.commit()
#     #     return redirect('/')
#     # except:
#     #     return 'There was a problem deleting that task'


# @app.route('/update/<int:id>', methods=['GET', 'POST'])
# def update(id):
#     b= 1
#     # task = Todo.query.get_or_404(id)
#
#     # if request.method == 'POST':
#     #     task.content = request.form['content']
#     #
#     #     try:
#     #         db.session.commit()
#     #         return redirect('/')
#     #     except:
#     #         return 'There was an issue updating your task'
#     #
#     # else:
#     #     return render_template('update.html', task=task)


if __name__ == "__main__":
    app.run(debug=True)
