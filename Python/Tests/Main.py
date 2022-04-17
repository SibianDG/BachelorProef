import requests
import json

multipart_form_data = {
    'audio_data': ('files', open('./files/1.wav', 'rb')),
}
values = {'extra_data': "1,1"}

response = requests.post('http://127.0.0.1:5000/receive_elderspeak', files=multipart_form_data, data=values)


print("####")
print(response)
print(response.content)
print(json.loads(response.content))
