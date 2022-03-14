#!/usr/bin/env python
# coding: utf-8

# In[1]:


import plotly.graph_objects as go
import urllib, json


# In[2]:


url = 'https://raw.githubusercontent.com/plotly/plotly.js/master/test/image/mocks/sankey_energy.json'
response = urllib.request.urlopen(url)
data = json.loads(response.read())

# override gray link colors with 'source' colors
opacity = 0.4
# change 'magenta' to its 'rgba' value to add opacity
data['data'][0]['node']['color'] = ['rgba(255,0,255, 0.8)' if color == "magenta" else color for color in data['data'][0]['node']['color']]
data['data'][0]['link']['color'] = [data['data'][0]['node']['color'][src].replace("0.8", str(opacity))
                                    for src in data['data'][0]['link']['source']]

fig = go.Figure(data=[go.Sankey(
    valueformat = ".0f",
    valuesuffix = "TWh",
    # Define nodes
    node = dict(
      pad = 15,
      thickness = 15,
      line = dict(color = "black", width = 0.5),
      label =  data['data'][0]['node']['label'],
      color =  data['data'][0]['node']['color']
    ),
    # Add links
    link = dict(
      source =  data['data'][0]['link']['source'],
      target =  data['data'][0]['link']['target'],
      value =  data['data'][0]['link']['value'],
      label =  data['data'][0]['link']['label'],
      color =  data['data'][0]['link']['color']
))])

fig.update_layout(title_text="Energy forecast for 2050<br>Source: Department of Energy & Climate Change, Tom Counsell via <a href='https://bost.ocks.org/mike/sankey/'>Mike Bostock</a>",
                  font_size=10)
fig.show()


# In[9]:


# data
label = ["ZERO", "ONE", "TWO", "THREE", "FOUR", "FIVE"]
source = [0, 0, 1, 1, 0]
target = [2, 3, 4, 5, 6]
value = [8, 2, 2, 8, 4]
# data to dict, dict to sankey
link = dict(source = source, target = target, value = value)
node = dict(label = label, pad=50, thickness=5)
data = go.Sankey(link = link, node=node)
# plot
fig = go.Figure(data)
fig.show()


# In[53]:


# data
label = ["Cities", "Women's March", "Anti Guns", "BLM", "No BLM"]
source = [0,0,0,0,1,1,1,2,2]
target = [1,2,3,4,2,3,4,3,4]
value =  [351,296,166,122,324,21,6, 573,47]
# data to dict, dict to sankey
link = dict(source = source, target = target, value = value)
node = dict(label = label, pad=40, thickness=30)
data = go.Sankey(link = link, node=node, orientation='v')
# plot
fig = go.Figure(data)
fig.show()


# In[54]:


# data
label = ["Cities", "Women's March", "Anti Guns", "BLM", "No BLM"]
source = [0,1,1,1,2,2]
target = [4,2,3,4,3,4]
value =  [122,324,21,6, 573,47]
# data to dict, dict to sankey
link = dict(source = source, target = target, value = value)
node = dict(label = label, pad=40, thickness=30)
data = go.Sankey(link = link, node=node, orientation='v')
# plot
fig = go.Figure(data)
fig.show()


# In[ ]:




