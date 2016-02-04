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

dbFileName = modulePath + 'weatherstation.db'
db = DBHelper(dbFileName)

args = cgi.FieldStorage()
# print 'len = ' + str(len(args))
if len(args) == 0:
    print
    print 'Hello'
elif method in args:
    if args[method].value == 'last':
        print "Content-type: application/json"
        print
        print (json.JSONEncoder().encode(db.getLast()))
    elif args[method].value == 'all':
        print "Content-type: application/json"
        print
        print (json.JSONEncoder().encode(db.getAll()))


db.close()

# if 'qwe' in args:
#     print args['qwe'].value
# if 'mtd' in args:
#     print 'method ' + args['mtd'].value


