#!/usr/bin/env python
# coding: utf-8

# In[36]:


fn = '/Users/nealcaren/Documents/GitHub/fightordie/_build/html/index.html'


# In[37]:


with open(fn,'r') as infile:
    html = infile.read()
    
html = html.replace("<h1>Dare you Fight<a", "<h1>Dare you Fight: W.E.B. Du Bois in The Crisis<a")
html = html.replace("<h1>Dare you Fight</h1>", "<h1>Dare you Fight:<br>W.E.B. Du Bois in The Crisis</h1>")


# In[38]:


start = html.find('<div class="section" id="table-of-contents">')
stop = start + 6 + html[39032:].find('</div>')

toc = html[start:stop]

html = html.replace(toc, '\n')


# In[39]:


with open(fn,'w') as outfile:
    outfile.write(html)


# In[43]:


toc_fn = '/Users/nealcaren/Documents/GitHub/fightordie/_build/html/toc.html'
with open(toc_fn,'r') as infile:
    toc_html = infile.read()
toc_html = toc_html.replace('<p>PLACEHOLDER</p>', toc)


# In[44]:


toc_html


# In[ ]:




