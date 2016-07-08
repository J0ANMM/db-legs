#!/bin/python

import sqlite3
import json
from collections import OrderedDict
import re
import datetime

### Function definitions ###
def dict_factory(cur, row):
    d = {}
    for idx, col in enumerate(cur.description):
        d[col[0]] = row[idx]
    return d

def filter_db(database):
    connection.row_factory = dict_factory

    cur = connection.cursor()
    cur.execute('''CREATE TABLE filt_legs AS
    SELECT route_name, departure_datetime, arrival_datetime, departure_station, arrival_station, price
    FROM legs WHERE departure_station = ? AND arrival_station = ? AND departure_datetime >= ? AND departure_datetime <= ?
    ORDER BY departure_datetime ASC''',
    (departure_station, arrival_station, departure_date + ' 00:00', departure_date + ' 23:59'))

    cur.execute('''CREATE TABLE output AS
    SELECT filt_legs.route_name, filt_legs.departure_datetime, filt_legs.arrival_datetime,
    filt_legs.departure_station, dep_stop.stop_name AS dep_st_name, filt_legs.arrival_station,
    arr_stop.stop_name AS arr_st_name, filt_legs.price
    FROM filt_legs
        JOIN stops dep_stop ON filt_legs.departure_station = dep_stop.stop_id
        JOIN stops arr_stop ON filt_legs.arrival_station = arr_stop.stop_id
    ORDER BY departure_datetime ASC''')

    connection.commit()

    cur.execute('''SELECT route_name, departure_datetime, arrival_datetime,
    departure_station, dep_st_name, arrival_station, arr_st_name, price
    FROM output
    ORDER BY departure_datetime ASC
    ''')

    results = cur.fetchall()
    return results

def sort_json(json_string):
    #sorts json to desired order
    sort_order = ['route_name', 'departure_station', 'dep_st_name', 'arrival_station', 'arr_st_name',
    'departure_datetime', 'arrival_datetime', 'price']
    json_ordered = [OrderedDict(sorted(item.iteritems(), key=lambda (k, v): sort_order.index(k)))
                    for item in json_string]
    return json.dumps(json_ordered, indent=4, separators=(',', ': '))


### End of funtion definition ###

#name of DB created in part1
DB = "./GFTS.sqlite"

connection = sqlite3.connect(DB)
cur = connection.cursor()

cur.execute('DROP TABLE IF EXISTS filt_legs')
cur.execute('DROP TABLE IF EXISTS output')

# departure_station = 8002549 #Example: Hamburg Hbf
print '----'
print 'Codes for main stations in Germany are:'
print 'Berlin Hbf: 8098160'
print 'Munich Hbf: 8000261'
print 'Hamburg Hbf: 8002549'
print 'Frankfurt(Main) Hbf: 8000105'
print 'Stuttgart Hbf: 8000096'
print 'Duesseldorf Hbf: 8000085'
print 'Koeln Hbf: 8000207'
print 'Dresden Hbf: 8010085'
print 'Hannover Hbf: 8000152'
print ' '
print 'A complete list of codes can be found in the following link:'
print 'https://github.com/J0ANMM/db-legs/blob/master/stops.txt'
print '----'
print ' '

departure_station = raw_input('+ Write departure_station code: ')
if ( len(departure_station) < 1 ):
    departure_station = 8002549 #Hamburg Hbf given as default departure_station
    print 'Value given by default:', departure_station
cur.execute('SELECT stop_id, stop_name FROM stops WHERE stop_id = ?', (departure_station, ))
in_db = cur.fetchone()
if in_db is None:
    exit('***** ERROR!!! Code not in database *****')
else:
    print 'Station is:', in_db[1]
    print ' '

arrival_station = raw_input('+ Write arrival_station code: ')
if ( len(arrival_station) < 1 ):
    arrival_station = 8000105 #Frankfurt(Main)Hbf given as default arrival_station
    print 'Value given by default:', arrival_station
cur.execute('SELECT stop_id, stop_name FROM stops WHERE stop_id = ?', (arrival_station, ))
in_db = cur.fetchone()
connection.commit()
if in_db is None:
    exit('***** ERROR!!! Code not in database *****')
else:
    print 'Station is:', in_db[1]
    print ' '
# departure_date = '2016-08-20' #Example of date
departure_date = raw_input('+ Write departure_date (YYYY-MM-DD): ')
if ( len(departure_date) < 1 ):
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    departure_date = str(tomorrow) #tomorrow given as default departure_date
    print 'Value given by default:', departure_date
    print ' '
match = re.search(r'\d\d\d\d-\d\d-\d\d', departure_date)
if match is None:
    exit('***** ERROR!!! Date is not in the appropriate format: YYYY-MM-DD *****')
else:
    pass
cur.execute('''SELECT DISTINCT departure_datetime FROM legs
WHERE departure_datetime >= ? AND departure_datetime <= ?''',
(departure_date + ' 00:00', departure_date + ' 23:59'))
in_db = cur.fetchone()
if in_db is None:
    exit('***** ERROR!!! Date not in database *****')
else:
    pass

json_unordered = filter_db(DB)
print sort_json(json_unordered)

cur.execute('DROP TABLE IF EXISTS filt_legs')
cur.close()
