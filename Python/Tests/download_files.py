#!/usr/bin/env python
# coding: utf-8

# In[6]:


import pandas as pd


# In[7]:


df = pd.read_csv('./files/Verzamelen_data_voor_Nursery_Sp2022-04-15_09_16_24.csv')


# In[8]:


df = df.drop(columns=["Submission Date", "Voor we beginnen zouden we graag jouw geslacht weten. Wat is je geslacht?", "Voice Recorder.8", "Type a question"])


# In[ ]:





# In[16]:


links = []
df = df.fillna(0)
for rowIndex, row in df.iterrows(): #iterate over rows
    for columnIndex, value in row.items():
        if value != 0:
            links.append(value)


# In[17]:


print(links)


# In[21]:


import urllib.request


# In[22]:


i = 1
for link in links:
    urllib.request.urlretrieve(link, f'./downloads/{i}.mp3')


# In[ ]:
