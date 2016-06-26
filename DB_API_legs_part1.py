### Deutsche Bahn ###

'''
Documentation:
http://data.deutschebahn.com/apis/fahrplan/

Location:
https://open-api.bahn.de/bin/rest.exe/location.name?authKey=xxx&lang=de&input=Frankfurt&format=json

Departures:
https://open-api.bahn.de/bin/rest.exe/departureBoard?authKey=xxx&lang=de&id=008000105&date=2016-08-01&time=07%3a00&format=json
'''

#Part 1 of the code to obtain legs from the information
#available in DB API
#Part 1 gets all the stations.

import sqlite3
from datetime import datetime
import json
import urllib
import time
from dateutil.relativedelta import relativedelta

############## Functions ##############

def spchar(s):
    #Converts special charts such as u with umlaut from Unicode to ASCII

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


def parselocations(fh):
    #Function to parse the json data obtained from API DB for locations service
    #Returns a list of stations
    conn = sqlite3.connect('api_db.sqlite')
    cur = conn.cursor()
    #Get the info for each field (parse)
    j = json.loads(fh)
    stations = j['LocationList']['StopLocation']
    #initialise list_of_stations
    list_of_stations = []

    for station in stations:
        #get value for each field
        id = station['id']
        stationname = spchar(station['name'])
        geocode_lat = station['lat']
        geocode_lon = station['lon']

        ########## Create tuple ##########
        #include all data in a tuple
        """station_tuple structure[
                (id
                stationname
                geocode_lat
                geocode_lon),
                (id
                stationname
                geocode_lat
                geocode_lon),...
                ]"""
        station_tuple = (id, stationname, geocode_lat, geocode_lon)
        #create list of stations as a list of tuples
        list_of_stations.append(station_tuple)
    cur.close()
    return list_of_stations

############## End of functions ##############

#SQLITE
conn = sqlite3.connect('api_db.sqlite')
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS stations')
cur.execute('DROP TABLE IF EXISTS legs')
cur.execute('DROP TABLE IF EXISTS errors')

cur.execute('''
CREATE TABLE stations (
	id	TEXT NOT NULL PRIMARY KEY,
	stationname TEXT NOT NULL,
	cityname TEXT,
	geocode_lat NUMERIC,
	geocode_lon NUMERIC)
''')

api_pw = 'xxx' #insert here you DB API password

#If search_list starts with 'A', there is a result of station called 'Amburgo' with same id
#as Hamburg Hbf, but as it would come first, name in SQL would be 'Amburgo', instead of 'Hamburg'.
search_list = ['Hamburg',
'A','B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'N',
'M', 'O', 'P', 'R', 'S', 'T', 'U', 'V', 'W', 'Z']

for item in search_list:
	station_url = 'https://open-api.bahn.de/bin/rest.exe/location.name?authKey=%s&lang=de&input=%s&format=json' % (api_pw, item)
	print 'Retrieving', station_url
	uh = urllib.urlopen(station_url)
	data = uh.read()
	list_of_stations = parselocations(data)
	print '******************************'

	for station in list_of_stations:
		id = str(station[0])
		stationname = spchar(unicode(station[1]))
		geocode_lat = str(station[2])
		geocode_lon = str(station[3])


		cur.execute('SELECT id FROM stations WHERE id = ? ', (id, ))
		res = cur.fetchone()

        #if station is already in the database --> do nothing
		#otherwise, station will be inserted
		if res:
			pass
		else:
			cur.execute('''INSERT INTO stations (id, stationname, geocode_lat, geocode_lon)
        	VALUES (?, ?, ?, ?)''',(id, stationname, geocode_lat, geocode_lon))
	conn.commit() #without this statement no values are inserted into the last table of the code

	time.sleep(1)

print "Stations imported to SQLite Database"

cur.close()
