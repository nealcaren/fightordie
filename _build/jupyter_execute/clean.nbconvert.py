#!/usr/bin/env python
# coding: utf-8

# In[1]:


fn = '/Users/nealcaren/Documents/GitHub/fightordie/_build/html/index.html'


# In[2]:


with open(fn,'r') as infile:
    html = infile.read()
    
html = html.replace("<h1>Dare you Fight<a", "<h1>Dare you Fight: W.E.B. Du Bois in The Crisis<a")
html = html.replace("<h1>Dare you Fight</h1>", "<h1>Dare you Fight:<br>W.E.B. Du Bois in The Crisis</h1>")


# In[3]:


with open(fn,'w') as outfile:
    outfile.write(html)


# In[ ]:




