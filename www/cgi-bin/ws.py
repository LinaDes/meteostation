#!/usr/bin/python
# - *- coding: utf- 8 - *-
import sys
import os
import json
modulePath = os.path.dirname(__file__) + '/../../'
sys.path.append(modulePath)
import cgi
from dbhelper import DBHelper

method = 'mtd'
version = 'version'
minThr = 'min'
maxThr = 'max'

dbFileName = modulePath + 'weatherstation.db'
db = DBHelper(dbFileName)

def makeJSON(records):
    return json.JSONEncoder().encode({'sensors': db.getSensors(), 'records': records})

args = cgi.FieldStorage()
# print 'len = ' + str(len(args))
if len(args) == 0:
    print
    print 'Hello'
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
        print (json.JSONEncoder().encode({version: 1}))


db.close()

# if 'qwe' in args:
#     print args['qwe'].value
# if 'mtd' in args:
#     print 'method ' + args['mtd'].value


