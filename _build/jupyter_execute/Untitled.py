#!/usr/bin/env python
# coding: utf-8

# In[2]:


from glob import glob


# In[5]:


mds = glob('**/*.md', recursive=True)


# In[18]:


def crisis_swap(text):
    if '**The Crisis**' in text:
        text = text.replace('**The Crisis**','<span style="font-variant:small-caps;">The Crisis</span>')
        print('Small capped')
    if '**Crisis**' in text:
        text = text.replace('**Crisis**','<span style="font-variant:small-caps;">Crisis</span>')
        print('Small capped')  
    if 'THE CRISIS' in  text:
        text = text.replace('THE CRISIS','<span style="font-variant:small-caps;">The Crisis</span>')
    
    text = text.replace('NATIONAL ASSOCIATION FOR THE ADVANCEMENT OF COLORED PEOPLE', 
                       '<span style="font-variant:small-caps;">National Association for the Advancement of Colored People</span>')
    
    return text


# In[13]:


def clean(fn):
    with open(fn, 'r') as infile:
        text = infile.read()
        
    text = crisis_swap(text)
    
    with open(fn, 'w') as outfile:
        outfile.write(text)
        


# In[21]:


fn = '/Users/nealcaren/Documents/GitHub/fightordie/Volumes/07/03/fightordie.md'


# In[22]:


clean(fn)


# In[ ]:




