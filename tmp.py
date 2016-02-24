#!/usr/bin/python
# - *- coding: utf- 8 - *-
__author__ = 'Andrew Kalinin'

from dbhelper import DBHelper

# dbFileName = 'weatherstation.db'
dbFileName = 'genweather.db'

db = DBHelper(dbFileName)

# for raw in db.getAll():
#     print raw
# print

# lastRec = db.getLast()
# print lastRec.keys()

print

for raw in db.getSensors():
    for i in raw.keys():
        print raw[i],
    print

# for raw in db.getInterval(1454599872, 1454599965):
#     print raw

db.close()
