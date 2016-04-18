#!/usr/bin/python
#- *- coding: utf- 8 - *-
import time
from datetime import datetime
from dbhelper import DBHelper

dbFileName = 'genweather.db'
db = DBHelper(dbFileName)


# now = time.time()
# dtnow = datetime.fromtimestamp(now)
# hours = datetime.fromtimestamp(now).hour
# print 'now',
# print dtnow
# print 'hours = ' + str(hours)
# ndt = datetime(dtnow.year, dtnow.month, dtnow.day, dtnow.hour)
# print ndt
# begin = time.mktime(ndt.timetuple())
# print begin
# print datetime.fromtimestamp(begin - 3600)
# print datetime.fromtimestamp(begin - 1)
# print

db.updateAvgTables()
db.updateAllRecordsView()
db.close()


# #!/usr/bin/python
# #- *- coding: utf- 8 - *-
# import math
# from protocol import Protocol
#
# deviceAddress = 0
# serialPort = '/dev/ttyUSB0'
# baudRate = 9600
# logEnabled = False
#
# device = Protocol(serialPort, baudRate, logEnabled)
# if device.ping(deviceAddress):
#     pressure, sernumP = device.getPressure(deviceAddress)
#     if 10 < pressure < 1000:
#         print ('Pressure - ' + str(pressure) + ' mmHg')
#     humidity, sernumH = device.getHumidity(deviceAddress)
#     if not math.isnan(humidity):
#         print ('Humidity - ' + str(humidity) + '%')
#     values = device.getTemp(deviceAddress)
#     i = 1
#     for (temperature, sn) in values:
#         print ('T' + str(i) + ' - ' + "%.1f" % temperature + ' C, sensor'),
#         device.printPacket(sn)
#         i += 1
# device.close()

# #!/usr/bin/python
# # - *- coding: utf- 8 - *-
# import sys
# import os
# import json
# import cgi
# import time
#
# from dbhelper import DBHelper
#
# method = 'mtd'
# version = 'version'
# minThr = 'min'
# maxThr = 'max'
#
# dbFileName = 'weatherstation.db'
# # dbFileName = modulePath + 'genweather.db'
# db = DBHelper(dbFileName)
#
# def makeJSON(records):
#     return json.JSONEncoder().encode({'sensors': db.getSensors(), 'records': records})
#
# if True:
#     sensors = db.getSensors()
#     records = db.getLast()
#     print 'Content-Type: text/html; charset=utf-8'
#     print
#     defaulthtml = """
#     <title>Метеостанция</title>
#     <h1>Погода</h1>
#     <hr>"""
#     defaulthtml += '<P>' + time.strftime("%d.%m.%Y %H:%M", time.localtime(records[0]['time'])) + '</P>'
#     defaulthtml += '<table border=0>'
#     for i in range(1, len(sensors) + 1):
#         if records[0][str(i)] is not None:
#             defaulthtml += '<tr>'
#             defaulthtml += '<td>' + str(sensors[i - 1]['id']) + '</td>'
#             defaulthtml += '<td>' + sensors[i - 1]['type'] + '</td>'
#             defaulthtml += '<td>' + sensors[i - 1]['description'] + '</td>'
#             defaulthtml += '<td>' + sensors[i - 1]['place'] + '</td>'
#             defaulthtml += '<td>' + "%.1f" % records[0][str(i)] + '</td>'
#             defaulthtml += '<td>' + sensors[i - 1]['valuename'] + '</td>'
#             defaulthtml += '</tr>'
#     defaulthtml += '<p><a href="sensors.py">Датчики</a></p>'
#     print defaulthtml
# # elif method in args:
# #     if args[method].value == 'last':
# #         print "Content-type: application/json"
# #         print
# #         print (makeJSON(db.getLast()))
# #     elif args[method].value == 'all':
# #         print "Content-type: application/json"
# #         print
# #         print (makeJSON(db.getAll()))
# #     elif args[method].value == 'interval':
# #         if minThr in args:
# #             if maxThr in args:
# #                 print "Content-type: application/json"
# #                 print
# #                 print (makeJSON(db.getInterval(args[minThr].value, args[maxThr].value)))
# #     elif args[method].value == version:
# #         print "Content-type: application/json"
# #         print
# #         print (json.JSONEncoder().encode({version: db.getDBVersion()}))
#
# db.close()
#
#
