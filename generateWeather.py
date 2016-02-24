#!/usr/bin/python
# - *- coding: utf- 8 - *-
__author__ = 'Andrew Kalinin'

import random
import time
from math import *
from dbhelper import DBHelper

dbFileName = 'genweather.db'

termSensorType = 1
pressureSensorType = 2
humiditySensorType = 3
pSn = 1
hSn = 2
tsn1 = 3
tsn2 = 4
tsn3 = 5

nums = 105121
# 1487087638
# 1455551638
# 31536000
# 86400
db = DBHelper(dbFileName)
currenttime = time.time()

for i in range(0, nums):
    h = 50 + 40 * sin(2 * pi * i / (nums / 12))
    p = 760 + 40 * sin(2 * pi * i / (nums / 365))
    t1 = 35 * sin(2 * pi * i / nums) + 7.5 * sin(2 * pi * 365 * i / nums) + random.uniform(-3, 3)
    t2 = 24 + 4 * sin(2 * pi * 12 * i / nums)
    t3 = t1 + random.uniform(0, 2)
    pressureSensorId = db.getSensorId(pressureSensorType, pSn)
    db.storeValue(currenttime, p, pressureSensorId)
    humiditySensorID = db.getSensorId(humiditySensorType, hSn)
    db.storeValue(currenttime, h, humiditySensorID)
    termSensorId = db.getSensorId(termSensorType, tsn1)
    db.storeValue(currenttime, t1, termSensorId)
    termSensorId = db.getSensorId(termSensorType, tsn2)
    db.storeValue(currenttime, t2, termSensorId)
    termSensorId = db.getSensorId(termSensorType, tsn3)
    db.storeValue(currenttime, t3, termSensorId)
    currenttime += 300
db.close()
