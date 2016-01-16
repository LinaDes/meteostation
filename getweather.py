#!/usr/bin/python
# - *- coding: utf- 8 - *-
__author__ = 'Andrew Kalinin'
from protocol import Protocol
import sys
import time
import sqlite3

def getSensorId(cursor, sensorType, sernum):
    cursor.execute('SELECT _id FROM sensors WHERE sernum=?', (sernum,))
    selres = cursor.fetchall()
    sensorId = -1
    if len(selres) > 0:
        sensorId = selres[0][0]
    else:
        cursor.execute('SELECT _id FROM sensortypes WHERE type=?', (sensorType,))
        sensorTypeId = cursor.fetchone()[0]
        cursor.execute('INSERT INTO sensors (type, sernum, description, place) VALUES (?,?,?,?)', (sensorTypeId, sernum, '', ''))
        cursor.execute('SELECT _id FROM sensors WHERE sernum=?', (sernum,))
        sensorId = cursor.fetchone()[0]
    return sensorId

deviceAddress = 0
serialPort = '/dev/ttyUSB0'
baudRate = 9600
termSensor = 'Датчик температуры'
pressureSensor = 'Датчик давления'
logEnabled = True

if len(sys.argv) == 3:
    serialPort = sys.argv[1]
    baudRate = sys.argv[2]
    deviceAddress = sys.argv[3]
    logEnabled = sys.argv[4]
elif len(sys.argv) == 1:
    print ('Command line: getweather.py serial_port serial_speed')
    print ('Trying with serial_port = ' + serialPort + ' and serial_speed = ' + str(baudRate))
else:
    print ('Command line: getweather.py serial_port serial_speed')
    sys.exit(1)

currenttime = time.time()

dbconnect = sqlite3.connect('test.db')
dbconnect.text_factory = str
cursor = dbconnect.cursor()

cursor.execute('CREATE TABLE IF NOT EXISTS sensortypes' +
               '(_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,' +
               'type TEXT NOT NULL)')
cursor.execute('SELECT type FROM sensortypes')
if len(cursor.fetchall()) == 0:
    cursor.execute('INSERT INTO sensortypes (type) VALUES (?)', (termSensor,))
    cursor.execute('INSERT INTO sensortypes (type) VALUES (?)', (pressureSensor,))
cursor.execute('CREATE TABLE IF NOT EXISTS sensors' +
               '(_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,' +
               'type INTEGER NOT NULL,' +
               'sernum TEXT,' +
               'description TEXT NOT NULL,' +
               'place TEXT NOT NULL,' +
               'FOREIGN KEY (type) REFERENCES sensortypes(_id))')
cursor.execute('CREATE TABLE IF NOT EXISTS metering' +
               '(_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,' +
               'time INTEGER NOT NULL,' +
               'value REAL NOT NULL,' +
               'sensorid INTEGER NOT NULL,' +
               'FOREIGN KEY (sensorid) REFERENCES sensors(_id))')

device = Protocol(serialPort, baudRate, logEnabled)
if device.ping(deviceAddress):
    pressure, sernum = device.getPressure(deviceAddress)
    print ('Pressure - ' + str(pressure) + ' mmHg, sensor')
    pressureSensorId = getSensorId(cursor, pressureSensor, sernum)
    cursor.execute('INSERT INTO metering (time, value, sensorid) VALUES (?,?,?)', (currenttime, pressure, pressureSensorId))
    numbers = ord(device.getNumbersOfSensors(deviceAddress))
    for i in range(1, numbers+1, 1):
        temperature, sn = device.getTempFromSensorN(0, i)
        print ('T' + str(i) + ' - ' + "%.1f" % temperature + ' C, sensor'),
        device.printPacket(sn)
        termSensorId = getSensorId(cursor, termSensor, sn)
        cursor.execute('INSERT INTO metering (time, value, sensorid) VALUES (?,?,?)', (currenttime, temperature, termSensorId))

dbconnect.commit()


