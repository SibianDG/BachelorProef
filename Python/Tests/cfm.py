import json
import os

import pandas as pd
import seaborn as sn
import matplotlib.pyplot as plt

arr = os.listdir('./files/jotform/')
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
        if v["expexted"] != v["result"]:
            l.append(k)
            m = confusion_matrices[k]
            m[int(v["result"])][int(v["expexted"])] += 1
            confusion_matrices[k] = m
        elif v["expexted"] == 0:
            m = confusion_matrices[k]
            m[1][1] += 1
            confusion_matrices[k] = m
        elif v["expexted"] == 1:
            m = confusion_matrices[k]
            m[0][0] += 1
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
