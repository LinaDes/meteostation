# - *- coding: utf- 8 - *-

import sqlite3
import time
from datetime import datetime

class DBHelper:

    dbconnect = None
    cursor = None

    version = 1

    def __init__(self, fileName):
        self.dbconnect = sqlite3.connect(fileName)
        self.dbconnect.text_factory = str
        self.cursor = self.dbconnect.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS dbversion' +
                            '(_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,' +
                            'time INTEGER NOT NULL,' +
                            'version INTEGER NOT NULL)')
        self.cursor.execute('SELECT version FROM dbversion')
        if len(self.cursor.fetchall()) == 0:
            self.cursor.execute('INSERT INTO dbversion (time, version) VALUES (?,?)', (int(time.time()), self.version))
        self.cursor.execute('CREATE TABLE IF NOT EXISTS sensortypes' +
                            '(_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,' +
                            'type TEXT,' +
                            'valuename TEXT)')
        self.cursor.execute('SELECT type FROM sensortypes')
        if len(self.cursor.fetchall()) == 0:
            self.cursor.execute('INSERT INTO sensortypes (type, valuename) VALUES (?,?)', ('Температура', 'град. С'))
            self.cursor.execute('INSERT INTO sensortypes (type, valuename) VALUES (?,?)', ('Давление', 'мм рт. ст.'))
            self.cursor.execute('INSERT INTO sensortypes (type, valuename) VALUES (?,?)', ('Влажность', '%'))
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
        self.cursor.execute('CREATE TABLE IF NOT EXISTS hourlyrecords' +
                            '(time INTEGER PRIMARY KEY NOT NULL)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS dailyrecords' +
                            '(time INTEGER PRIMARY KEY NOT NULL)')
        self.cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS "avgday" on dailyrecords (time ASC)')
        self.cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS "avghour" on hourlyrecords (time ASC)')
        self.cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS "mid" on metering (_id ASC)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS "time" on metering (time ASC)')
        self.cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS "sid" on sensors (_id ASC)')
        self.cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS "stid" on sensortypes (_id ASC)')

    def updateAvgTables(self):
        self.cursor.execute('SELECT MAX(_id) FROM sensors')
        number = self.cursor.fetchone()[0]
        self.cursor.execute('SELECT * FROM hourlyrecords ORDER BY ROWID ASC LIMIT 1')
        columnnamelist = [tuple[0] for tuple in self.cursor.description]
        if number > (len(columnnamelist)-1):
            for i in range(len(columnnamelist), number+1):
                self.cursor.execute('ALTER TABLE hourlyrecords ADD COLUMN v%s REAL' % str(i))
                self.cursor.execute('ALTER TABLE dailyrecords ADD COLUMN v%s REAL' % str(i))
        self.cursor.execute('SELECT MIN(time) FROM metering')
        minrealtime = self.cursor.fetchone()[0]
        if minrealtime is not None:
            self.cursor.execute('SELECT MAX(time) FROM metering')
            maxrealtime = self.cursor.fetchone()[0]
            self.cursor.execute('SELECT MAX(time) FROM hourlyrecords')
            maxhourlyavgtime = self.cursor.fetchone()[0]
            self.cursor.execute('SELECT MAX(time) FROM dailyrecords')
            maxdailyavgtime = self.cursor.fetchone()[0]
            firsthourtime = 1
            firstdaytime = 1
            if maxhourlyavgtime is None:
                maxhourlyavgtime = minrealtime
                firsthourtime = 0
            if maxdailyavgtime is None:
                maxdailyavgtime = minrealtime
                firstdaytime = 0
            begin = datetime.fromtimestamp(float(maxhourlyavgtime))
            end = datetime.fromtimestamp(float(maxrealtime))
            cyclebegin = datetime(begin.year, begin.month, begin.day, begin.hour+firsthourtime)
            cycleend = datetime(end.year, end.month, end.day, end.hour)
            for i in range(int(time.mktime(cyclebegin.timetuple())), int(time.mktime(cycleend.timetuple()))-1, 3600):
                self.cursor.execute('SELECT AVG(time) FROM metering WHERE time >= %s AND time <= %s' % (str(i), str(i+3599)))
                if self.cursor.fetchone()[0] is None:
                    continue
                insert = 'INSERT INTO hourlyrecords (time'
                select = 'SELECT CAST(AVG(time) AS INTEGER)'
                for v in range(1, number+1):
                    insert += ', v%s' % str(v)
                    select += ', AVG(CASE WHEN sensorid=%s THEN value ELSE NULL END)' % str(v)
                insert += ') '
                select += ' FROM metering WHERE time >= %s AND time <= %s' % (str(i), str(i+3599))
                self.cursor.execute(insert + select)
            begin = datetime.fromtimestamp(float(maxdailyavgtime))
            end = datetime.fromtimestamp(float(maxrealtime))
            cyclebegin = datetime(begin.year, begin.month, begin.day+firstdaytime)
            cycleend = datetime(end.year, end.month, end.day)
            for i in range(int(time.mktime(cyclebegin.timetuple())), int(time.mktime(cycleend.timetuple()))-1, 86400):
                self.cursor.execute('SELECT AVG(time) FROM metering WHERE time >= %s AND time <= %s' % (str(i), str(i+85399)))
                if self.cursor.fetchone()[0] is None:
                    continue
                insert = 'INSERT INTO dailyrecords (time'
                select = 'SELECT CAST(AVG(time) AS INTEGER)'
                for v in range(1, number+1):
                    insert += ', v%s' % str(v)
                    select += ', AVG(CASE WHEN sensorid=%s THEN value ELSE NULL END)' % str(v)
                insert += ') '
                select += ' FROM metering WHERE time >= %s AND time <= %s' % (str(i), str(i+85399))
                query = insert + select
                self.cursor.execute(query)


    def __makeDict(self, raw):
        res = {'time': raw[0]}
        for i in range(2, len(raw)+1):
            res[str(i-1)] = raw[i - 1]
        return res

    def getSensorId(self, sensorType, sernum):
        self.cursor.execute('SELECT _id FROM sensors WHERE sernum=? AND type=?', (sernum, sensorType))
        selres = self.cursor.fetchall()
        # sensorId = -1
        if len(selres) > 0:
            sensorId = selres[0][0]
        else:
            self.cursor.execute('INSERT INTO sensors (type, sernum, description, place) VALUES (?,?,?,?)', (sensorType, sernum, '', ''))
            self.cursor.execute('SELECT _id FROM sensors WHERE sernum=? AND type=?', (sernum, sensorType))
            sensorId = self.cursor.fetchone()[0]
        return sensorId

    def storeValue(self, time, value, sensorId):
        self.cursor.execute('INSERT INTO metering (time, value, sensorid) VALUES (?,?,?)', (int(time), value, sensorId))

    def getLast(self):
        self.cursor.execute('SELECT MAX(_id) FROM sensors')
        number = self.cursor.fetchone()[0]
        query = 'SELECT time'
        for i in range(1, number+1):
            query += ', (SELECT value FROM metering WHERE sensorid=%s AND time=m.time)' % str(i)
        query += ' FROM metering m WHERE time=(SELECT MAX(time) FROM metering) GROUP BY time'
        self.cursor.execute(query)
        return [self.__makeDict(self.cursor.fetchone()), ]

    def getInterval(self, minTime = None, maxTime = None):
        self.cursor.execute('SELECT MAX(_id) FROM sensors')
        number = self.cursor.fetchone()[0]
        query = 'SELECT time'
        for i in range(1, number+1):
            query += ', (SELECT value FROM metering WHERE sensorid=%s AND time=m.time)' % str(i)
        if minTime is not None and maxTime is not None:
            query += ' FROM metering m WHERE (time >= ? AND time <= ?) GROUP BY time'
            self.cursor.execute(query, (minTime, maxTime))
        else:
            query += ' FROM metering m GROUP BY time ORDER BY time'
            self.cursor.execute(query)
        return [self.__makeDict(raw) for raw in self.cursor.fetchall()]

    def updateAllRecordsView(self):
        self.cursor.execute('SELECT MAX(_id) FROM sensors')
        number = self.cursor.fetchone()[0]
        self.cursor.execute('DROP VIEW IF EXISTS allrecords')
        query = 'CREATE VIEW allrecords AS SELECT time time'
        for i in range(1, number+1):
            query += ', max(CASE WHEN sensorid=%s THEN value ELSE NULL END) v%s' % (str(i), str(i))
        query += ' FROM metering GROUP BY time ORDER BY time'
        self.cursor.execute(query)
        return

    def getAll(self):
        return self.getInterval()

    def getSensors(self):
        self.cursor.execute('SELECT s._id, st.type, s.sernum, s.description, s.place, st.valuename FROM sensors s, sensortypes st WHERE s.type=st._id ORDER BY s._id')
        res = []
        for raw in self.cursor.fetchall():
            res.append({'id': raw[0],
                        'type': raw[1],
                        'sernum': ' '.join("%X" % ord(c) if ord(c) > 0x0f else '0' + "%X" % ord(c) for c in raw[2]),
                        'description': raw[3],
                        'place': raw[4],
                        'valuename': raw[5]})
        return res

    def updateSensor(self, sensorid, description, place):
        self.cursor.execute('UPDATE sensors SET description = ?, place = ? WHERE _id = ?', (description, place, sensorid))

    def getDBVersion(self):
        self.cursor.execute('SELECT version FROM dbversion WHERE _id=(SELECT MAX(_id) FROM dbversion)')
        return self.cursor.fetchone()[0]

    def close(self):
        self.dbconnect.commit()

