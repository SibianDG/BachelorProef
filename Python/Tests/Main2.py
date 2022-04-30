import requests
import json
import statistics

import os
import re

import pandas as pd
import seaborn as sn
import matplotlib.pyplot as plt

true_false_dict = {'0': False, '1': True}

arr = os.listdir('./files/jotform/')
print(arr)
d = dict()

for person in range(1, 10 + 1):
    p = 'person' + str(person).zfill(2)
    print(f"Busy with {p} for normal")
    r = re.compile(f"{p}_sub[0-9]_0_0_0\.mp3")
    newlist = list(filter(r.match, arr))
    loudness = []
    pitch = []
    for f in newlist:
        multipart_form_data = {
            'audio_data': ('files', open('./files/jotform/' + f, 'rb')),
        }
        response = requests.post('http://127.0.0.1:5000/receive_normal', files=multipart_form_data)
        j = json.loads(response.content)
        loudness.append(j['loudness'])
        pitch.append(j['pitch'])
    d[p] = {'loudness': round(statistics.mean(loudness), 2), 'pitch': round(statistics.mean(pitch), 2)}

print(d)
d2 = dict()
files_filter = dict()

abc = dict()

for person in range(1, 10 + 1):
    p = 'person' + str(person).zfill(2)
    print(f"{p} analysing")
    person_list = [x for x in arr if x.startswith(p)]

    for f in person_list:
        multipart_form_data = {
            'audio_data': ('files', open('./files/jotform/' + f, 'rb')),
        }
        # values = {'extra_data': f'{d[p]["loudness"]},{d[p]["pitch"]}'}
        response = requests.post('http://127.0.0.1:5000/receive_normal', files=multipart_form_data)  # , data=values)
        j = json.loads(response.content)
        test = dict()
        abc[f] = {'loudness': [d[p]['loudness'], j['loudness']], 'pitch': [d[p]['pitch'], j['pitch']]}

with open('abc.json', 'w') as outfile:
    json.dump(abc, outfile)

file = []
pitch_n = []
pitch_es = []
loudness_n = []
loudness_es = []

for k, v in abc.items():
    file.append(k)
    pitch_n.append(v['pitch'][0])
    pitch_es.append(v['pitch'][1])
    loudness_n.append(v['loudness'][0])
    loudness_es.append(v['loudness'][1])

df = pd.DataFrame(
    data={'file': file, 'pitch_n': pitch_n, 'pitch_es': pitch_es, 'loudness_n': loudness_n, 'loudness_es': loudness_es})
df.to_csv('abc.csv', index=False)
