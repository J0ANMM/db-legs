# db-legs
### Aim:
Create a clear and simple output of legs bewteen two cities from the data available in Deutsche Bahn API.

### Instructions:
Code is split in 3 files / parts:
* Part 1: Creates a table called 'stations' (SQLite) with all stations available in DB API
* Part 2: Obtains all legs given a specific date and time. Two additional tables (SQLite) are created. One called 'legs' registers all the legs, and another one called 'errors' register all the errors during the import and parsing. Note that in the tests performed this takes almost 1 hour and around 70.000 rows are obtained.
* Part 3: From table 'legs' output JSON with all legs between two stations.

Output would look like this:

    [
    {
        "id": "20160801_ICE973_8002549_8000105",
        "route_name": "ICE973",
        "departure_station": "8002549",
        "arrival_station": "8000105",
        "departure_datetime": "2016-08-01 07:01:00",
        "arrival_datetime": "2016-08-01 11:00:00",
        "price": "?"
    },
    {
        "id": "20160801_IC2023_8002549_8000105",
        "route_name": "IC2023",
        "departure_station": "8002549",
        "arrival_station": "8000105",
        "departure_datetime": "2016-08-01 07:46:00",
        "arrival_datetime": "2016-08-01 14:12:00",
        "price": "?"
    },
    ...

### Important
Code works, but it can definitely be optimized and improved. Any contribution to make it better is more than welcome! :)


### Additional information:
Deutsche Bahn API:
* http://data.deutschebahn.com/apis/fahrplan/
* https://s3.eu-central-1.amazonaws.com/opendata-dbsiat/static/apis/fahrplan/Fpl-API-Doku-Open-Data-BETA-0_81_2.pdf

In GitHub:
* https://github.com/dbopendata/db-fahrplan-api
* https://github.com/fredlockheed/db-fv-gtfs/releases (GTFS)
