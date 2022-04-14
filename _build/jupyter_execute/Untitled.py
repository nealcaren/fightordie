#!/usr/bin/env python
# coding: utf-8

# In[28]:


from glob import glob
import re


# In[5]:


mds = glob('**/*.md', recursive=True)


# In[23]:


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


def cite_fix(text):
    if '*Citation:* "' in text:
        text = text.replace('*Citation:* "','*Citation:* Du Bois, W.E.B. "')


# In[24]:


def clean(fn):
    with open(fn, 'r') as infile:
        text = infile.read()
        
    text = crisis_swap(text)
    
    with open(fn, 'w') as outfile:
        outfile.write(text)
        


# In[25]:


fn = '/Users/nealcaren/Documents/GitHub/fightordie/Volumes/07/03/fightordie.md'


# In[26]:


clean(fn)


# In[27]:


sample = '*Citation:* "Fight or Die" Editorial. 1914. *The Crisis*. 7(3): 133-134.'


# In[38]:


text = sample
py = re.findall('Editorial\. (19..)', text)
if len(py) == 1:
    pubyear = py[0]
    


# In[64]:


items = re.findall('\*Citation:\* "(.*?)" Editorial\. (19.*?)\. (\*The Crisis\*\..*?\.)', sample)


# In[72]:


title = items[0][0]
year = items[0][1]
pub = items[0][2]
new = f'*Citation: Du Bois, W.E.B. {year}. "{title}."  '
new


# In[66]:


new


# In[68]:





# In[ ]:




