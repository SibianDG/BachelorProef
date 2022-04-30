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

for person in range(1, 10+1):
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

for person in range(1, 10+1):
    p = 'person' + str(person).zfill(2)
    print(f"{p} analysing")
    person_list = [x for x in arr if x.startswith(p)]

    for f in person_list:
        multipart_form_data = {
            'audio_data': ('files', open('./files/jotform/' + f, 'rb')),
        }
        values = {'extra_data': f'{d[p]["loudness"]},{d[p]["pitch"]}'}
        response = requests.post('http://127.0.0.1:5000/receive_elderspeak', files=multipart_form_data, data=values)
        j = json.loads(response.content)
        test = dict()
        test['verkleinwoord'] = {'expexted': true_false_dict[f[14]], 'result': True if "text-danger" in j['verkleinwoorden'] else False}
        test['loudness'] = {'expexted': true_false_dict[f[16]], 'result': False if "Stiller" in j['loudness'] else True}
        test['pitch'] = {'expexted': true_false_dict[f[18]], 'result': False if "Lager" in j['pitch'] else True}
        files_filter[f] = test
        d2[f] = j

print(d2)
with open('json_resut.json', 'w') as outfile:
    json.dump(d, outfile)

with open('test_results.json', 'w') as outfile:
    json.dump(files_filter, outfile)

with open('d2.json', 'w') as outfile:
    json.dump(d2, outfile)


for file, d in files_filter.items():
    l = list()
    for k, v in d.items():
        if v["expexted"] != v["result"]:
            l.append(k)
    if len(l) != 0:
        print(f'Het systeem heeft in file {file} de volgende fouten gedetecteerd: {l}')

with open('test_results.json') as json_file:
    data = json.load(json_file)

print(data)
print(len(data))

confusion_matrices = {"verkleinwoord": [[0, 0], [0, 0]], "pitch": [[0, 0], [0, 0]],
                      "loudness": [[0, 0], [0, 0]]}  # predicted == row

for file, d in data.items():
    l = list()
    i = 0
    for k, v in d.items():
        m = confusion_matrices[k]
        if v["expexted"] != v["result"]:
            l.append(k)
            m[int(v["result"])][int(v["expexted"])] += 1
        elif v["expexted"] == 0:
            m[0][0] += 1
        elif v["expexted"] == 1:
            m[1][1] += 1
        confusion_matrices[k] = m

    if len(l) != 0:
        print(f'Het systeem heeft in file {file} de volgende fouten gedetecteerd: {l}')

print(confusion_matrices)


classes = ["True", "False"]

for k, v in confusion_matrices.items():
    df_cfm = pd.DataFrame(v, index=classes, columns=classes)
    plt.figure(figsize=(10, 7))
    plt.title(k)
    # plt.ylabel('Voorspelde waarde', fontsize=18)
    cfm_plot = sn.heatmap(df_cfm, annot=True)
    cfm_plot.set_xlabel('Echte waarde')
    cfm_plot.set_ylabel('Voorspelde waarde')

    cfm_plot.figure.savefig(f"./plots/cfm_{k}.png")
