import requests
import json
import statistics

import os
import re

true_false_dict = {'0': False, '1': True}

arr = os.listdir('./files/jotform/')
print(arr)
print(len(arr))
for person in range(1, 10+1):
    p = 'person' + str(person).zfill(2)
    filtered_list = [x for x in arr if x.startswith(p)]
    print(filtered_list)