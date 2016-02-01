#!/usr/bin/python
# - *- coding: utf- 8 - *-

import cgi

form = cgi.FieldStorage()
print('Content-type: text/html')
html = """
<TITLE>tst3.py</TITLE>
<H1>Greetings</H1>
<HR>
<P>%s</P>
<HR>"""
if not 'item' in form:
    print(html % 'empty')
else:
    print(html % ('Hello, %s.' % form['item'].value))
