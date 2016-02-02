#!/usr/bin/python
# - *- coding: utf- 8 - *-
__author__ = 'Andrew Kalinin'

from dbhelper import DBHelper

dbFileName = 'weatherstation.db'

db = DBHelper(dbFileName)

for raw in db.getAll():
    print raw

db.close()
