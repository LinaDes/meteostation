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
            self.cursor.execute('INSERT INTO sensortypes (type) VALUES (?)', ('',))
            self.cursor.execute('INSERT INTO sensortypes (type) VALUES (?)', ('',))
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

    def getAll(self):
        self.cursor.execute('SELECT max(_id) from sensors')
        number = self.cursor.fetchone()[0]
        query = 'select time'
        for i in range(1, number+1):
            query += ', (select value from metering where sensorid=%s and time=m.time)' % str(i)
        query += ' from metering m group by time'
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def close(self):
        self.dbconnect.commit()

