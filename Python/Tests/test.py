import json
import os

arr = os.listdir('./files/jotform/')
with open('test_results.json') as json_file:
    data = json.load(json_file)

confusion_matrices = {"verkleinwoord": [[0, 0], [0, 0]], "pitch": [[0, 0], [0, 0]], "loudness": [[0, 0], [0, 0]]} #predicted == row

for file, d in data.items():
    l = list()
    i = 0
    for k, v in d.items():
        if v["expexted"] != v["result"]:
            l.append(k)
            m = confusion_matrices[k]
            m[int(v["result"])][int(v["expexted"])] += 1
            confusion_matrices[k] = m
    if len(l) != 0:
        print(f'Het systeem heeft in file {file} de volgende fouten gedetecteerd: {l}')

print(confusion_matrices)

for file in arr:
    if file not in data.keys():
        for k in confusion_matrices.keys():
            m = confusion_matrices[k]
            m[int(file[14])][int(file[14])] += 1
            m[int(file[16])][int(file[18])] += 1
            m[int(file[18])][int(file[18])] += 1
            confusion_matrices[k] = m
print(confusion_matrices)
