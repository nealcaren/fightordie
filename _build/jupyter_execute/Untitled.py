#!/usr/bin/env python
# coding: utf-8

# In[2]:


from glob import glob


# In[5]:


mds = glob('**/*.md', recursive=True)


# In[12]:


def crisis_swap(text):
    if '**The Crisis**' in text:
        text = text.replace('**The Crisis**','<span style="font-variant:small-caps;">The Crisis</span>')
        print('Small capped')
    if '**Crisis**' in text:
        text = text.replace('**Crisis**','<span style="font-variant:small-caps;">Crisis</span>')
        print('Small capped')    
    return text


# In[13]:


def clean(fn):
    with open(fn, 'r') as infile:
        text = infile.read()
        
    text = crisis_swap(text)
    
    with open(fn, 'w') as outfile:
        outfile.write(text)
        


# In[14]:


fn = '/Users/nealcaren/Documents/GitHub/fightordie/Volumes/41/08/dr_dubois_resigns.md'


# In[15]:


clean(fn)


# In[ ]:




