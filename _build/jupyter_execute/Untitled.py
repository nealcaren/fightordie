#!/usr/bin/env python
# coding: utf-8

# In[28]:


from glob import glob
import re


# In[5]:


mds = glob('**/*.md', recursive=True)


# In[103]:


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
    new_txt = []
    for line in text.splitlines():
        if '*Citation:* ' in line and "Editorial." in line and 'The Crisis' in line :

            text = text.replace('*Citation:* "','*Citation:* Du Bois, W.E.B. "')
            
            items = re.findall('\*Citation:\* "(.*?)" Editorial\. (19.*?)\. (\*The Crisis\*\..*?\.)', line)
            title = items[0][0]
            year = items[0][1]
            pub = items[0][2]
            new = f'*Citation:* Du Bois, W.E.B. {year}. "{title}." {pub}'
            new_txt.append(new)
            print('Cite fixed')
            
        elif '*Citation:*' in line and "Editorial." in line:
            items = re.findall('\*Citation:\* "(.*?)" (19.*?)\. Editorial\. (.*?\.)', line)
            title = items[0][0]
            year = items[0][1]
            pub = items[0][2]
            new = f'*Citation:* Du Bois, W.E.B. {year}. "{title}" *The Crisis* {pub}'
            new_txt.append(new)
            print('Cite fixed')
            
        else:
            new_txt.append(line)
            
    return '\n'.join(new_txt)


# In[116]:


def clean(fn):
    with open(fn, 'r') as infile:
        text = infile.read()
        
    text = crisis_swap(text)
    
    text = text.replace('N[*****]', 'N*****')
    text = text.replace('N[******]', 'N*****')



    '''try:
        text = cite_fix(text)
    except IndexError:
        print(f'Cite issue with {fn}')
    '''
    with open(fn, 'w') as outfile:
        outfile.write(text)
        


# In[113]:


fn = '/Users/nealcaren/Documents/GitHub/fightordie/Volumes/21/02/unreal_campaign.md'


# In[114]:


clean(fn)


# In[100]:


line = '*Citation:* "The New Crisis." 1925. Editorial.  30(1):7-9.'

print(new)


# In[115]:


for fn in mds:
    clean(fn)


# In[64]:





# In[74]:





# In[75]:


new


# In[68]:





# In[ ]:




