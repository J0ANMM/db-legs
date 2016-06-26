### Deutsche Bahn ###
'''
Documentation:
http://data.deutschebahn.com/apis/fahrplan/

Location:
https://open-api.bahn.de/bin/rest.exe/location.name?authKey=xxx&lang=de&input=Frankfurt&format=json

Departures:
https://open-api.bahn.de/bin/rest.exe/departureBoard?authKey=xxx&lang=de&id=008000105&date=2016-08-01&time=07%3a00&format=json
'''

import sqlite3
from datetime import datetime
import json
import urllib
import requests
import time
from dateutil.relativedelta import relativedelta
import itertools
import time
start_time = time.time()

#### FUNCTION definitions ####
def spchar(s):
    """Converts special charts such as u with umlaut from Unicode to ASCII"""
    #a_umlaut
    s = s.replace('\u00e4','ae') #a-umlaut = \u00e4 ==> ae
    a_umlaut = u'\u00e4'.encode('utf-8').decode('utf-8')
    s = s.replace(a_umlaut,'ae') #a-umlaut = \u00e4 ==> ae
    s = s.replace('\u00c4','AE') #A-umlaut = \u00c4 ==> AE
    A_umlaut = u'\u00c4'.encode('utf-8').decode('utf-8')
    s = s.replace(A_umlaut,'AE') #A-umlaut = \u00c4 ==> AE

    #o_umlaut
    s = s.replace('\u00f6','oe') #o-umlaut = \u00f6 ==> oe
    o_umlaut = u'\u00f6'.encode('utf-8').decode('utf-8')
    s = s.replace(o_umlaut,'oe') #o-umlaut = \u00f6 ==> oe
    s = s.replace('\u00d6','OE') #O-umlaut = \u00d6 ==> OE
    O_umlaut = u'\u00d6'.encode('utf-8').decode('utf-8')
    s = s.replace(O_umlaut,'OE') #o-umlaut = \u00d6 ==> OE

    #u_umlaut
    s = s.replace('\u00fc','ue') #u-umlaut = \u00fc ==> ue
    u_umlaut = u'\u00fc'.encode('utf-8').decode('utf-8')
    s = s.replace(u_umlaut,'ue') #u-umlaut = \u00fc ==> ue
    s = s.replace('\u00dc','UE') #U-umlaut = \u00dc ==> UE
    U_umlaut = u'\u00dc'.encode('utf-8').decode('utf-8')
    s = s.replace(U_umlaut,'UE') #u-umlaut = \u00dc ==> UE

    #eszett
    s = s.replace('\u00df','ss') #eszett = \u00df ==> ss
    eszett = u'\u00df'.encode('utf-8').decode('utf-8')
    s = s.replace('\u1e9e','SS') #Eszett = \u1e9e ==> SS
    Eszett = u'\u1e9e'.encode('utf-8').decode('utf-8')

    return s


def parseDepartureBoard(fh):
    #Get the info for each field (parse)
    j = json.loads(fh)
    #initialise list_of_refs
    list_of_refs = []
    try:
        departures = j['DepartureBoard']['Departure']
        #time.sleep(0.1)
        #API currently gives a list of tuples if there is more than one route from
        #that station, or only a tuple if there is just one route. Issue raised in GitHub.
        #Until it is solve, this IF block is needed...
        if isinstance (departures, dict):
            print 'Dict detected!!!!'
            route_code = departures['name']
            dep_ref = departures['JourneyDetailRef']['ref']
            ref_tuple = (route_code, dep_ref)
            #create list of refs as a list of tuples
            list_of_refs.append(ref_tuple)
        else:
            for departure in departures:
                #get value for each field
                route_code = departure['name']
                dep_ref = departure['JourneyDetailRef']['ref']

                ########## Create tuple ##########
                #include all data in a tuple
                """ref_tuple structure[
                        (route_code
                        dep_ref),
                        (route_code
                        dep_ref),...
                        ]"""
                ref_tuple = (route_code, dep_ref)
                #create list of refs as a list of tuples
                list_of_refs.append(ref_tuple)
    except KeyError:
        #register error in case the json structure is not the expected one
        print '**********************************'
        print 'ATENTION!!! Unable to parse this station. JSON structure not as expected: no departures in station'
        print 'Related station is:', departure_station
        print 'Related link is:', dep_url
        print '**********************************'
        conn = sqlite3.connect('api_db.sqlite')
        cur = conn.cursor()
        cur.execute('SELECT count FROM errors WHERE id = ? ', ('no_departures-' + route_name, ))
        in_count = cur.fetchone()
        if in_count:
            error_count = in_count[0] + 1
            cur.execute('''REPLACE INTO errors (id, error_type, station, link, count)
            VALUES (?, ?, ?, ?, ?)''',('no_departures-' + departure_station, 'no_departures',
            departure_station, dep_url, error_count))
        else:
            cur.execute('''INSERT INTO errors (id, error_type, station, link, count)
            VALUES (?, ?, ?, ?, ?)''',('no_departures-' + departure_station, 'no_departures', departure_station, dep_url, 1))
        conn.commit() #without this statement no values are inserted into the last table of the code
        cur.close()
    return list_of_refs


def parseJourneyDetail(fh):
    j = json.loads(fh)
    #print 'inside parseJourneyDetail function'
    try:
        journey_stops = j['JourneyDetail']['Stops']['Stop']
    except Exception as e:
        pass #register it!

    list_of_stops = []

    for journey_stop in journey_stops:
        station_name = journey_stop['name']
        station_id = journey_stop['id']
        route_idx = journey_stop['routeIdx']
        try:
            dep_time = journey_stop['depTime']
            dep_date = journey_stop['depDate']
        except KeyError as e:
            dep_time = 'xx'
            dep_date = 'xx'
        try:
            arr_time = journey_stop['arrTime']
            arr_date = journey_stop['arrDate']
        except KeyError as e:
            arr_time = 'xx'
            arr_date = 'xx'
        #time.sleep(0.1)
        stops_tuple = (station_name, station_id, route_idx, arr_time, arr_date, dep_time, dep_date)
        list_of_stops.append(stops_tuple)
    return list_of_stops


def combinations(source):
    result = []
    for p1 in range(len(source)):
            for p2 in range(p1+1,len(source)):
                    result.append([source[p1],source[p2]])
    return result


def printExecTime(start_time, inter_time):
    #function that prints the execution time of the code from the begining.
    #variable init_time must be set that the beginning of the code, so the count starts
    #use following code: start_time = time.time()
    #inter_time (optional) is one intermediate_time. It must be included wherever
    #the intermediate time count is supposed to start
    #use following code: inter_time = time.time()
    if inter_time is None:
        pass
    else:
        execution_time = time.time() - intermediate_time
        m, s = divmod(execution_time, 60)
        m = int(m)
        s = round(s,3)
        print("Execution time for " + dep_station_name + " (" +
        departure_station + "): --- %s minutes and %s seconds ---" % (m, s))

    total_execution_time = time.time() - start_time
    m_tot, s_tot = divmod(total_execution_time, 60)
    m_tot = int(m_tot)
    s_tot = round(s_tot,3)
    print("Total cumulated execution time: --- %s minutes and %s seconds ---" % (m_tot, s_tot))


######### MAIN PROGRAM ########

#SQLITE
conn = sqlite3.connect('api_db.sqlite')
cur = conn.cursor()
cur.execute('DROP TABLE IF EXISTS legs')
cur.execute('DROP TABLE IF EXISTS errors')

cur.execute('''
CREATE TABLE legs (
	id	TEXT NOT NULL PRIMARY KEY,
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
    link TEXT NOT NULL,
    count INTEGER)
''')

conn.commit() #without this statement no values are inserted into the last table of the code

#### Input #####
departure_date = '2016/08/01' #Format: yyyy/mm/dd
departure_time = '07:00' #Format hh:mm
api_pw = 'xxx' #insert here you DB API password

departure_day = departure_date[8:]
departure_month = departure_date[5:7]
departure_year = departure_date[0:4]
departure_hour = departure_time[0:2]
departure_minute = departure_time[3:5]

#Get of station id's from SQLite list. (Note that fetchall gives a list of tuples).
cur.execute('SELECT id FROM stations')
station_ids = cur.fetchall()
print 'Stations in the list are:'
for station in station_ids:
    print station

#loop for each id/station of the list
for station in station_ids:
    intermediate_time = time.time()
    departure_station = station[0]
    dep_url = 'https://open-api.bahn.de/bin/rest.exe/departureBoard?authKey=%s&lang=de&id=%s&date=%s-%s-%s&time=%s%%3a%s&format=json' \
    % (api_pw, departure_station, departure_year, departure_month, departure_day, departure_hour, departure_minute)
    cur.execute('SELECT stationname FROM stations WHERE id = ? ', (departure_station, ))
    dep_station_name = cur.fetchone()[0]
    print '+++++++++++++++++++++++++++++++++++++++++++++'
    print 'Loading DepartureBoard for station ', departure_station, '-', dep_station_name
    print dep_url
    time.sleep(3)
    r = requests.get(dep_url)
    dep_board_json = r.text
    list_of_refs = parseDepartureBoard(dep_board_json)
    #loop for each reference/journey of one station
    for ref in list_of_refs:
        route_name = ref[0].replace(" ", "")
        route_ref = ref[1]

        #If station is already in the database --> nothing
        #otherwise, station will be inserted
        cur.execute('SELECT route_name FROM legs WHERE route_name = ? ', (route_name, ))
        res1 = cur.fetchone()
        cur.execute('SELECT route_name FROM errors WHERE route_name = ? ', (route_name, ))
        res2 = cur.fetchone()

        if res1 or res2:
            print 'Route', route_name, 'already in'
        else:
            try:
                time.sleep(1)
                jd = requests.get(route_ref)
                journey_detail = jd.text
                list_of_stops = parseJourneyDetail(journey_detail)
                error = False
            except UnboundLocalError:
                error = True

            if error is True:
                print '**********************************'
                print 'ATENTION!!! Unable to parse this route. JSON input might be empty...'
                print 'Related route is:', ref[0]
                print 'Related link is:', ref[1]
                print '**********************************'

                cur.execute('SELECT count FROM errors WHERE id = ? ', ('no_json-' + route_name, ))
                in_count = cur.fetchone()
                if in_count:
                    error_count = in_count[0] + 1
                    cur.execute('''REPLACE INTO errors (id, error_type, route_name, link, count)
                    VALUES (?, ?, ?, ?, ?)''',('no_json-' + route_name, 'no_json',
                    route_name, ref[1], error_count))
                else:
                    cur.execute('''INSERT INTO errors (id, error_type, route_name, link, count)
                    VALUES (?, ?, ?, ?, ?)''',('no_json-' + route_name, 'no_json', route_name, ref[1], 1))

            else:
                list_of_stop_ids = []
                for stop in list_of_stops:
                    stop_id = stop[1]
                    list_of_stop_ids.append(stop_id)

                pairings = combinations(list_of_stop_ids)
                count_legs = 0
                for pair in pairings:
                    departure_stop = [item for item in list_of_stops if item[1] == pair[0]]
                    arrival_stop = [item for item in list_of_stops if item[1] == pair[1]]
                    dep_station = departure_stop[0][1]
                    dep_time = departure_stop[0][5]
                    dep_date = departure_stop[0][6]
                    arr_station = arrival_stop[0][1]
                    arr_time= arrival_stop[0][3]
                    arr_date = arrival_stop[0][4]
                    price = '?'

                    departure_datetime = datetime.strptime(dep_date + ' ' + dep_time, '%Y-%m-%d %H:%M') # ISO Format?
                    arrival_datetime = datetime.strptime(arr_date + ' ' + arr_time, '%Y-%m-%d %H:%M')
                    #departure_datetime = To_ISO_datetime(dep_date, dep_time)
                    #arrival_datetime = To_ISO_datetime(arr_date, arr_time)
                    dep_year = str(departure_datetime.year)
                    dep_month = int(departure_datetime.month)
                    if dep_month < 10: dep_month = str('0' + str(departure_datetime.month))
                    else: dep_month = str(departure_datetime.month)
                    dep_day = int(departure_datetime.day)
                    if dep_day < 10: dep_day = str('0' + str(departure_datetime.day))
                    else: dep_day = str(departure_datetime.day)

                    #create table id
                    table_id = (departure_year + dep_month + dep_day +
                    '_' + route_name + '_' + dep_station + '_' + arr_station)

                    #some routes are stopping twice at the same station
                    #(like ICE1218 at FFM Airport)
                    cur.execute('SELECT id FROM legs WHERE id = ? ', (table_id, ))
                    itsin = cur.fetchone()
                    if itsin:
                        cur.execute('SELECT count FROM errors WHERE id = ? ', ('station_duplicated-' + route_name, ))
                        in_count = cur.fetchone()
                        if in_count:
                            error_count = in_count[0] + 1
                            cur.execute('''REPLACE INTO errors (id, error_type, route_name, link, station, count)
                            VALUES (?, ?, ?, ?, ?, ?)''',('station_duplicated-' + route_name, 'station_duplicated',
                            route_name, ref[1], dep_station + ' or ' + arr_station, error_count))
                        else:
                            print '**********************************'
                            print ('ATENTION!!! One station is duplicated in this route. For more info check errors table in SQLite')
                            print 'Related route is:', ref[0]
                            print 'Related link is:', ref[1]
                            print '**********************************'
                            cur.execute('''REPLACE INTO errors (id, error_type, route_name, link, station, count)
                            VALUES (?, ?, ?, ?, ?, ?)''',('station_duplicated-' + route_name, 'station_duplicated',
                            route_name, ref[1], dep_station + ' or ' + arr_station, 1))
                    else:
                        cur.execute('''INSERT INTO legs (id, route_name, departure_station,
                        arrival_station, departure_datetime, arrival_datetime, price)
                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                        (table_id, route_name, dep_station, arr_station, departure_datetime, arrival_datetime, '?'))
                    count_legs = count_legs + 1
                print route_name + ' inserted in DB (' + str(count_legs) + ' legs)'
            conn.commit() #without this statement no values are inserted into the last table of the code
    printExecTime(start_time, intermediate_time)
cur.close()

print 'Import finished.'
#print 'See SQLite table errors for all import errors.'
