#!/usr/bin/env python
# coding: utf-8


from glob import glob

fns = glob('_build/html/**/*.html', recursive=True)

def clean(fn):
    with open(fn,'r') as infile:
        html = infile.read()

    ugh = " &#8212; Dare you Fight&amp;#58;&lt;br/&gt;W.E.B. Du Bois&lt;br/&gt;in The Crisis"

    html = html.replace(ugh,'')
    with open(fn,'w') as outfile:
        outfile.write(html)

for fn in fns:
    clean(fn)
