import requests
import json
import statistics

import os
import re

true_false_dict = {'0': False, '1': True}

arr = os.listdir('./files/jotform/')
print(arr)
d = dict()

for person in range(1, 10):
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

for person in range(1, 10):
    p = 'person' + str(person).zfill(2)
    print(f"Busy with {p} for elderspeak")
    r = re.compile(f"{p}[^.]+\.mp3")
    s = set(filter(r.match, arr))
    print("SET:")
    print(s)
    for f in s:
        multipart_form_data = {
            'audio_data': ('files', open('./files/jotform/' + f, 'rb')),
        }
        values = {'extra_data': f'{d[p]["loudness"]},{d[p]["pitch"]}'}
        response = requests.post('http://127.0.0.1:5000/receive_elderspeak', files=multipart_form_data, data=values)
        j = json.loads(response.content)
        test = dict()
        test['verkleinwoord'] = {'expexted': true_false_dict[f[14]], 'result': True if "<span>" in j['verkleinwoorden'] else False}
        test['loudness'] = {'expexted': true_false_dict[f[16]], 'result': False if "Stiller" in j['loudness'] else True}
        test['pitch'] = {'expexted': true_false_dict[f[18]], 'result': False if "Lager" in j['pitch'] else True}
        files_filter[f] = test
        d2[p] = j

print(d2)
with open('json_resut.json', 'w') as outfile:
    json.dump(d, outfile)

with open('test_results.json', 'w') as outfile:
    json.dump(files_filter, outfile)


for file, d in files_filter.items():
    l = list()
    for k, v in d.items():
        if v["expexted"] != v["result"]:
            l.append(k)
    if len(l) != 0:
        print(f'Het systeem heeft in file {file} de volgende fouten gedetecteerd: {l}')

