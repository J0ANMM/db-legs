#!/bin/python

import sqlite3
import datetime
import time

start_time = time.time()

path = 'GFTS/2016.0.1/'

### Functions definition ###
def parse_route_txt():
    def parse_route(l):
        l_split = l.split(',')
        route_id = l_split[0]
        route_name = l_split[2].replace(' ', '')
        route = (route_id, route_name)
        list_of_routes.append(route)

    list_of_routes = []
    with open(path + 'routes.txt') as f:
        next(f)
        for line in f:
            parse_route(line)
    return list_of_routes

def parse_trip_txt():
    def parse_trip(l):
        l_split = l.split(',')
        route_id = l_split[0]
        service_id = l_split[1]
        trip_id = l_split[2]
        trip_headsign = l_split[3]
        trip = (route_id, service_id, trip_id, trip_headsign)
        list_of_trips.append(trip)

    list_of_trips = []
    with open(path + 'trips.txt') as f:
        next(f)
        for line in f:
            parse_trip(line)
    return list_of_trips

def parse_calendar_dates_txt():
    def parse_calendar_dates(l):
        l_split = l.split(',')
        service_id = l_split[0]
        sdate = str(l_split[1])
        sdate = str(sdate[0:4]) + '-' + str(sdate[4:6]) + '-' + str(sdate[6:])
        exception_type = l_split[2]
        calendar_date = (service_id, sdate, exception_type)
        list_of_calendar_dates.append(calendar_date)

    list_of_calendar_dates = []
    with open(path + 'calendar_dates.txt') as f:
        next(f)
        for line in f:
            parse_calendar_dates(line)
    return list_of_calendar_dates

def parse_stop_times_txt():
    def parse_stop_times(l):
        l_split = l.split(',')
        trip_id = l_split[0]
        arrival_time = l_split[1].split(':')
        arrival_time = arrival_time[0] + ':' + arrival_time[1]
        departure_time = l_split[2].split(':')
        departure_time = departure_time[0] + ':' + departure_time[1]
        stop_id = l_split[3]
        stop_sequence = l_split[4]
        stop_time = (trip_id, arrival_time, departure_time, stop_id, stop_sequence)
        list_of_stop_times.append(stop_time)
    list_of_stop_times = []
    with open(path + 'stop_times.txt') as f:
        next(f)
        for line in f:
            parse_stop_times(line)
    return list_of_stop_times

def parse_stops_txt():
    def parse_stops(l):
        l_split = l.split(',')
        stop_id = l_split[0]
        stop_name = str(l_split[1])
        stop_lat = l_split[2]
        stop_lon = l_split[3]
        stop_timezone = l_split[4]
        stop = (stop_id, stop_name, stop_lat, stop_lon, stop_timezone)
        list_of_stops.append(stop)
    list_of_stops = []
    with open(path + 'stops.txt') as f:
        next(f)
        for line in f:
            parse_stops(line)
    return list_of_stops

def combinations(source):
    result = []
    for p1 in range(len(source)):
            for p2 in range(p1+1,len(source)):
                    result.append([source[p1],source[p2]])
    return result

### End of functions definition ###

# Parse txt files
list_of_routes = parse_route_txt()
print 'routes.txt parsed'

list_of_trips = parse_trip_txt()
print 'trips.txt parsed'

list_of_calendar_dates = parse_calendar_dates_txt()
print 'calendar_dates.txt parsed'

list_of_stop_times = parse_stop_times_txt()
print 'stop_times.txt parsed'

list_of_stops = parse_stops_txt()
print 'stops.txt parsed'


#SQLITE
conn = sqlite3.connect('GFTS.sqlite')
cur = conn.cursor()

cur.executescript('''
DROP TABLE IF EXISTS routes;
DROP TABLE IF EXISTS trips;
DROP TABLE IF EXISTS calendar_dates;
DROP TABLE IF EXISTS stop_times;
DROP TABLE IF EXISTS stops;
DROP TABLE IF EXISTS merge1;
DROP TABLE IF EXISTS merge2;
DROP TABLE IF EXISTS merge3;
DROP TABLE IF EXISTS legs;
DROP TABLE IF EXISTS errors
''')


cur.execute('''
CREATE TABLE routes (
	route_id	NUMERIC NOT NULL PRIMARY KEY,
	route_name TEXT NOT NULL
    )
''')

for route in list_of_routes:
    cur.execute('''INSERT INTO routes (route_id, route_name)
    VALUES (?, ?)''',(route[0], route[1]))
conn.commit()
print 'routes.txt imported in SQLite'


cur.execute('''
CREATE TABLE trips (
	route_id	NUMERIC NOT NULL,
	service_id NUMERIC NOT NULL,
    trip_id NUMERIC NOT NULL PRIMARY KEY,
    trip_headsign TEXT
    )
''')

for trip in list_of_trips:
    headsign = trip[3].decode('utf-8')
    #headsign = headsign.encode("utf-8")
    cur.execute('''INSERT INTO trips (route_id, service_id, trip_id, trip_headsign)
    VALUES (?, ?, ?, ?)''',(int(trip[0]), int(trip[1]), int(trip[2]), headsign))
conn.commit()
print 'trips.txt imported in SQLite'


cur.execute('''
CREATE TABLE calendar_dates (
	service_id NUMERIC NOT NULL,
	sdate TEXT NOT NULL,
    exception_type TEXT NOT NULL,
    PRIMARY KEY (service_id, sdate, exception_type)
    )
''')

for calendar_date in list_of_calendar_dates:
    cur.execute('''INSERT INTO calendar_dates (service_id, sdate, exception_type)
    VALUES (?, ?, ?)''',(calendar_date[0], calendar_date[1], calendar_date[2]))
conn.commit()
print 'calendar_dates.txt imported in SQLite'


cur.execute('''
CREATE TABLE stop_times (
    id INTEGER PRIMARY KEY,
	trip_id NUMERIC NOT NULL,
	arrival_time TEXT NOT NULL,
    departure_time TEXT NOT NULL,
    stop_id NUMERIC NOT NULL,
    stop_sequence NUMERIC NOT NULL
    )
''')

for stop_time in list_of_stop_times:
    cur.execute('''INSERT INTO stop_times (trip_id, arrival_time, departure_time, stop_id, stop_sequence)
    VALUES (?, ?, ?, ?, ?)''',(stop_time[0], stop_time[1], stop_time[2], stop_time[3], stop_time[4]))
conn.commit()
print 'stop_times.txt imported in SQLite'



cur.execute('''
CREATE TABLE stops (
	stop_id	NUMERIC NOT NULL PRIMARY KEY,
	stop_name TEXT NOT NULL,
	stop_lat TEXT,
	stop_lon TEXT,
    stop_timezone TEXT
    )
''')

for stop in list_of_stops:
    stop_name = stop[1].decode('utf-8')

    cur.execute('''INSERT INTO stops (stop_id, stop_name, stop_lat, stop_lon, stop_timezone)
    VALUES (?, ?, ?, ?, ?)''',(stop[0], stop_name, stop[2], stop[3], stop[4]))
conn.commit()
print 'stops.txt imported in SQLite'

##Create 'legs' table by merging the previous 3 tables in various steps

cur.execute('''
CREATE TABLE merge1 AS
SELECT routes.route_name, trips.service_id, trips.trip_id
FROM trips
INNER JOIN routes
ON routes.route_id = trips.route_id
''')
print 'SQL tables trips and routes merged'


cur.execute('''
CREATE TABLE merge2 AS
SELECT merge1.route_name, calendar_dates.sdate, merge1.trip_id
FROM merge1
LEFT JOIN calendar_dates
ON merge1.service_id = calendar_dates.service_id
''')
print 'SQL table calendar_dates merged'


cur.execute('''
CREATE TABLE merge3 AS
SELECT merge2.route_name, merge2.sdate, stop_times.arrival_time, stop_times.departure_time, stop_times.stop_id, stop_times.stop_sequence
FROM merge2
LEFT JOIN stop_times
ON merge2.trip_id = stop_times.trip_id
''')
print 'SQL table stop_times merged'


cur.execute('DROP TABLE IF EXISTS merge1')
cur.execute('DROP TABLE IF EXISTS merge2')

cur.execute('''
CREATE TABLE legs (
	id	INTEGER PRIMARY KEY,
    route_name TEXT NOT NULL,
	departure_datetime TEXT NOT NULL,
	arrival_datetime TEXT NOT NULL,
    departure_station TEXT NOT NULL,
    arrival_station TEXT NOT NULL,
	price NUMERIC)
''')

cur.execute('''
CREATE TABLE errors (
    id TEXT PRIMARY KEY,
    error_type TEXT NOT NULL,
    route_name	TEXT,
    station TEXT,
    link TEXT,
    count INTEGER)
''')

conn.commit()

## Combine stops for each route each day to get the legs

i = datetime.datetime.now()
today = i.strftime('%Y-%m-%d')

cur.execute('SELECT DISTINCT sdate FROM merge3 WHERE sdate >= ? ORDER BY date(sdate) ASC', (today, ))
dates = cur.fetchall()

print 'Fetching complete merged table'
print '...'

cur.execute('SELECT route_name, sdate, arrival_time, departure_time, stop_id FROM merge3 WHERE sdate >= ? ORDER BY date(sdate) ASC', (today, ))
all_stop_info = cur.fetchall()

for singledate in dates:
    intermediate_time = time.time()
    singledate = singledate[0]
    # filter by date
    stops = [item for item in all_stop_info if item[1] == singledate]

    #create what before was "routes"
    routes = []
    for stop in stops:
        route = stop[0]
        routes.append(route)
    set_routes = set(routes) #remove duplicates by converting a list to a set
    routes = list(set_routes)

    count_routes_imported = 0
    count_legs_imported = 0
    list_of_legs =[]

    for route_name in routes:
        list_of_stop_ids = []
        list_of_stops = [item for item in stops if item[0] == route_name]

        for stop in list_of_stops:
            stop_id = stop[4]
            list_of_stop_ids.append(stop_id)
        pairings = combinations(list_of_stop_ids)

        for pair in pairings:
            departure_stop = [item for item in list_of_stops if item[4] == pair[0]]
            arrival_stop = [item for item in list_of_stops if item[4] == pair[1]]
            dep_station = str(departure_stop[0][4])
            dep_time = departure_stop[0][3]
            dep_date = departure_stop[0][1]
            arr_station = str(arrival_stop[0][4])
            arr_time= arrival_stop[0][2]
            arr_date = arrival_stop[0][1]
            price = '?'
            departure_datetime = dep_date + ' ' + dep_time
            arrival_datetime = arr_date + ' ' + arr_time

            try:
                #create list of tuples and insert afterwards many in a batch, as it is much faster.
                leg = (route_name, dep_station, arr_station, departure_datetime, arrival_datetime, '?')
                list_of_legs.append(leg)
                count_legs_imported = count_legs_imported + 1

            except sqlite3.IntegrityError:
                cur.execute('SELECT id FROM legs WHERE id = ? ', (table_id, ))
                itsin = cur.fetchone()
                if itsin:
                    cur.execute('SELECT count FROM errors WHERE id = ? ', ('station_duplicated-' + route_name, ))
                    in_count = cur.fetchone()
                    if in_count:
                        error_count = in_count[0] + 1
                        cur.execute('''REPLACE INTO errors (id, error_type, route_name, station, count)
                        VALUES (?, ?, ?, ?, ?)''',('station_duplicated-' + route_name, 'station_duplicated',
                        route_name, dep_station + ' or ' + arr_station, error_count))
                    else:
                        print '**********************************'
                        print ('ATENTION!!! One station is duplicated in this route. For more info check errors table in SQLite')
                        print 'Related route is:', route_name
                        print '**********************************'
                        cur.execute('''REPLACE INTO errors (id, error_type, route_name, station, count)
                        VALUES (?, ?, ?, ?, ?)''',('station_duplicated-' + route_name, 'station_duplicated',
                        route_name, dep_station + ' or ' + arr_station, 1))
                        conn.commit()
                else:
                    break

        count_routes_imported = count_routes_imported + 1

    cur.executemany('''INSERT INTO legs (route_name, departure_station,
    arrival_station, departure_datetime, arrival_datetime, price)
    VALUES (?, ?, ?, ?, ?, ?)''', list_of_legs)
    conn.commit() #without this statement no values are inserted into the last table of the code

    #Print execution time
    execution_time = time.time() - intermediate_time
    m, s = divmod(execution_time, 60)
    m = int(m)
    s = round(s,3)
    print 'Data from', singledate, 'imported.'
    print 'Execution time for this date: %s minutes and %s seconds' % (m, s)
    print count_routes_imported, 'routes imported that contained', count_legs_imported, 'legs.'
    total_execution_time = time.time() - start_time
    m_tot, s_tot = divmod(total_execution_time, 60)
    m_tot = int(m_tot)
    s_tot = round(s_tot,3)
    print("Total cumulated execution time: --- %s minutes and %s seconds ---" % (m_tot, s_tot))
    print '++++++++++++++++++'

cur.execute('DROP TABLE IF EXISTS merge3')
cur.close()

print 'Import finished.'
