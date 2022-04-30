import requests
import json
import statistics

import os
import re

import pandas as pd

with open('abc.json') as json_file:
    abc = json.load(json_file)

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

df = pd.DataFrame(data={'file': file, 'pitch_n':pitch_n,'pitch_es':pitch_es, 'loudness_n':loudness_n, 'loudness_es':loudness_es})
df.to_csv('abc.csv', index=False)
