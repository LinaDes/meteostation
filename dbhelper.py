# - *- coding: utf- 8 - *-
__author__ = 'Andrew Kalinin'

import sqlite3

class DBHelper:

    dbconnect = None
    cursor = None

    def __init__(self, fileName):
        self.dbconnect = sqlite3.connect(fileName)
        self.dbconnect.text_factory = str
        self.cursor = self.dbconnect.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS sensortypes' +
                            '(_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,' +
                            'type TEXT)')
        self.cursor.execute('SELECT type FROM sensortypes')
        if len(self.cursor.fetchall()) == 0:
            self.cursor.execute('INSERT INTO sensortypes (type) VALUES (?)', ('temperature',))
            self.cursor.execute('INSERT INTO sensortypes (type) VALUES (?)', ('pressure',))
        self.cursor.execute('CREATE TABLE IF NOT EXISTS sensors' +
                            '(_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,' +
                            'type INTEGER NOT NULL,' +
                            'sernum TEXT,' +
                            'description TEXT NOT NULL,' +
                            'place TEXT NOT NULL,' +
                            'FOREIGN KEY (type) REFERENCES sensortypes(_id))')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS metering' +
                            '(_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,' +
                            'time INTEGER NOT NULL,' +
                            'value REAL NOT NULL,' +
                            'sensorid INTEGER NOT NULL,' +
                            'FOREIGN KEY (sensorid) REFERENCES sensors(_id))')

    def getSensorId(self, sensorType, sernum):
        self.cursor.execute('SELECT _id FROM sensors WHERE sernum=?', (sernum,))
        selres = self.cursor.fetchall()
        # sensorId = -1
        if len(selres) > 0:
            sensorId = selres[0][0]
        else:
            self.cursor.execute('INSERT INTO sensors (type, sernum, description, place) VALUES (?,?,?,?)', (sensorType, sernum, '', ''))
            self.cursor.execute('SELECT _id FROM sensors WHERE sernum=?', (sernum,))
            sensorId = self.cursor.fetchone()[0]
        return sensorId

    def recordValue(self, currenttime, value, sensorId):
        self.cursor.execute('INSERT INTO metering (time, value, sensorid) VALUES (?,?,?)', (currenttime, value, sensorId))

    def getLast(self):
        self.cursor.execute('SELECT MAX(_id) FROM sensors')
        number = self.cursor.fetchone()[0]
        query = 'SELECT time'
        for i in range(1, number+1):
            query += ', (SELECT value FROM metering WHERE sensorid=%s AND time=m.time)' % str(i)
        query += ' FROM metering m WHERE time=(SELECT MAX(time) FROM metering) GROUP BY time'
        self.cursor.execute(query)
        return self.__makeDict(self.cursor.fetchone())

    def __makeDict(self, raw):
        res = {'time': raw[0]}
        for i in range(2, len(raw)+1):
            res[str(i-1)] = raw[i - 1]
        return res

    def getInterval(self, minTime, maxTime):
        self.cursor.execute('SELECT MAX(_id) FROM sensors')
        number = self.cursor.fetchone()[0]
        query = 'SELECT time'
        for i in range(1, number+1):
            query += ', (SELECT value FROM metering WHERE sensorid=%s AND time=m.time)' % str(i)
        query += ' FROM metering m WHERE (time >= ? AND time <= ?) GROUP BY time'
        self.cursor.execute(query, (minTime, maxTime))
        res = []
        for raw in self.cursor.fetchall():
            res.append(self.__makeDict(raw))
        return res

    def getAll(self):
        self.cursor.execute('SELECT max(_id) from sensors')
        number = self.cursor.fetchone()[0]
        query = 'SELECT time'
        for i in range(1, number+1):
            query += ', (SELECT value FROM metering WHERE sensorid=%s AND time=m.time)' % str(i)
        query += ' FROM metering m GROUP BY time ORDER BY time'
        self.cursor.execute(query)
        res = []
        for raw in self.cursor.fetchall():
            res.append(self.__makeDict(raw))
        return res

    def getSensors(self):
        res = self.cursor.execute('SELECT s._id, st.type, s.sernum, s.description, s.place, s._id FROM sensors s, sensortypes st WHERE s.type=st._id')
        return res

    def close(self):
        self.dbconnect.commit()

