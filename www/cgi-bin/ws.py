#!/usr/bin/python
# - *- coding: utf- 8 - *-
import sys
import os
import json

import time

modulePath = os.path.dirname(__file__) + '/../../'
# modulePath = os.path.abspath('/home/weather') + '/'

sys.path.append(modulePath)
import cgi
from dbhelper import DBHelper

method = 'mtd'
version = 'version'
minThr = 'min'
maxThr = 'max'

# dbFileName = modulePath + 'weatherstation.db'
dbFileName = modulePath + 'genweather.db'
db = DBHelper(dbFileName)

def makeJSON(records):
    return json.JSONEncoder().encode({'sensors': db.getSensors(), 'records': records})

args = cgi.FieldStorage()
if len(args) == 0:
    sensors = db.getSensors()
    records = db.getLast()
    print 'Content-Type: text/html; charset=utf-8'
    print
    html = """
    <TITLE>Метеостанция</TITLE>
    <H1>Погода</H1>
    <HR>"""
    html += '<P>' + time.strftime("%d %B %Y %H:%M", time.localtime(records[0]['time'])) + '</P>'
    html += '<table border=1>'
    for i in range(1, len(sensors) + 1):
        html += '<tr>'
        html += '<td>' + str(sensors[i-1]['id']) + '</td><td>' + sensors[i-1]['type'] + '</td><td>' + "%.1f" % records[0][str(i)] + '</td><td>' + sensors[i-1]['valuename'] + '</td>'
        html += '</tr>'
    print html
elif method in args:
    if args[method].value == 'last':
        print "Content-type: application/json"
        print
        print (makeJSON(db.getLast()))
    elif args[method].value == 'all':
        print "Content-type: application/json"
        print
        print (makeJSON(db.getAll()))
    elif args[method].value == 'interval':
        if minThr in args:
            if maxThr in args:
                print "Content-type: application/json"
                print
                print (makeJSON(db.getInterval(args[minThr].value, args[maxThr].value)))
    elif args[method].value == version:
        print "Content-type: application/json"
        print
        print (json.JSONEncoder().encode({version: db.getDBVersion()}))

db.close()


