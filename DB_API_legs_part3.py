import sqlite3
import json
from collections import OrderedDict

DB = "./api_db.sqlite"
#provide id's for the desired departure and arrival stations
departure_station = 8002549 #Example: Hamburg Hbf
arrival_station = 8000105 #Example: Frankfurt Hbf


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_json():
    connection = sqlite3.connect(DB)
    connection.row_factory = dict_factory

    cursor = connection.cursor()
    cursor.execute('SELECT * FROM legs WHERE departure_station = ? 
    AND arrival_station = ?', (departure_station, arrival_station))
    results = cursor.fetchall()
    return results


def sort_json(json_string):
    #sorts json to desired order
    sort_order = ['id', 'route_name', 'departure_station', 'arrival_station', 
    'departure_datetime', 'arrival_datetime', 'price']
    json_ordered = [OrderedDict(sorted(item.iteritems(), key=lambda (k, v): sort_order.index(k)))
                    for item in json_string]
    return json.dumps(json_ordered, indent=4, separators=(',', ': '))

json_unordered = get_json()
print sort_json(json_unordered)
