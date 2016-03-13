#!/usr/bin/python
# - *- coding: utf- 8 - *-
import sys
import os
import cgi

modulePath = os.path.dirname(__file__) + '/../../'
# modulePath = os.path.abspath('/home/weather') + '/'
sys.path.append(modulePath)
from dbhelper import DBHelper

method = 'mtd'
sensorNumber = 'sensornumber'

dbFileName = modulePath + 'weatherstation.db'
# dbFileName = modulePath + 'genweather.db'
db = DBHelper(dbFileName)
args = cgi.FieldStorage()
if len(args) == 0:
    sensors = db.getSensors()
    print 'Content-Type: text/html; charset=utf-8'
    print
    sensorshtml = """
    <title>Метеостанция</title>
    <h1>Датчики</h1>
    <hr>
    <table border=0>
    <tr>
        <td> № </td>
        <td>Тип</td>
        <td> s/n </td>
        <td>Описание</td>
        <td>Место установки</td>
        <td>Ед. измерения</td>
    </tr>"""
    url = 'sensors.py?mtd=sensor&'
    for s in sensors:
        sensorshtml += '<tr>'
        sensorshtml += '<td>' + '<a href="' + url + sensorNumber + '=' + str(s['id']) + '">' + str(s['id'])     + '</a></td>'
        sensorshtml += '<td>' + '<a href="' + url + sensorNumber + '=' + str(s['id']) + '">' + s['type']        + '</a></td>'
        sensorshtml += '<td>' + '<a href="' + url + sensorNumber + '=' + str(s['id']) + '">' + s['sernum']      + '</a></td>'
        sensorshtml += '<td>' + '<a href="' + url + sensorNumber + '=' + str(s['id']) + '">' + s['description'] + '</a></td>'
        sensorshtml += '<td>' + '<a href="' + url + sensorNumber + '=' + str(s['id']) + '">' + s['place']       + '</a></td>'
        sensorshtml += '<td>' + '<a href="' + url + sensorNumber + '=' + str(s['id']) + '">' + s['valuename']   + '</a></td>'
        sensorshtml += '</tr>'
    print sensorshtml

elif method in args:
    if args[method].value == 'sensor':
        if sensorNumber in args:
            numstr = args[sensorNumber].value
            if numstr.isdigit():
                num = int(numstr) - 1
                sensors = db.getSensors()
                if 0 <= num <= len(sensors):
                    sensor = sensors[num]
                    sensorshtml = """<!DOCTYPE html>
                                    <html lang="en">
                                    <head>
                                    <meta charset="UTF-8">
                                    <title>Редактор</title>
                                    </head>
                                    <body>
                                    <H1>Корректировка датчика</H1>
                                    <hr>
                                    <form method=POST action="sensors.py">
                                        <B> № %s</B>
                                        <input type=text name=id value="%s" hidden>
                                        <B>Тип</B>
                                        <input type=text name=type value="%s" disabled>
                                        <B> s/n </B>
                                        <input type=text name=sernum value="%s" disabled>
                                        <B>Описание</B>
                                        <input type=text name=description value="%s">
                                        <B>Место установки</B>
                                        <input type=text name=place value="%s">
                                        <B>Ед. измерения</B>
                                        <input type=text name=valuename value="%s" disabled>
                                        <input type=submit name="save" value="Сохранить">
                                    </form>
                                    </body>
                                    </html>""" % (sensor['id'], sensor['id'], sensor['type'], sensor['sernum'], sensor['description'], sensor['place'], sensor['valuename'])
                    print 'Content-Type: text/html; charset=utf-8'
                    print
                    print sensorshtml

elif 'save' in args:
    description = cgi.escape(args['description'].value) if 'description' in args else ''
    place = cgi.escape(args['place'].value) if 'place' in args else ''
    sensorid = int(args['id'].value)

    print 'Content-Type: text/html; charset=utf-8'
    print
    db.updateSensor(sensorid, description, place)
    savehtml = """<!DOCTYPE html>
                  <html lang="en">
                  <head>
                  <meta charset="UTF-8">
                  <meta http-equiv="refresh" content="1;url=sensors.py">
                  <title>Редактор</title>
                  </head>"""
    print savehtml

db.close()
