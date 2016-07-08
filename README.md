# db-legs
### Aim:
Create a clear and simple output of legs bewteen two cities from the data available in Deutsche Bahn API.

### Instructions:
Since a [GTFS](https://github.com/fredlockheed/db-fv-gtfs) with all extracted data from the DB API has already been created (great job!), those files will be used here as input. This allows to increase the speed drastically, as all information is downloaded once and there is no need to pull information from the DB

Code is split in 2 files / parts:
* Part 1: Creates a table called 'legs' (SQLite) with all legs between two cities using the GFTS txt files
* Part 2: From table 'legs' output JSON with all legs between two stations.

Output would look like this:

    [
    {
        "route_name": "ICE571",
        "departure_station": "8002549",
        "dep_st_name": "Hamburg Hbf",
        "arrival_station": "8000105",
        "arr_st_name": "Frankfurt(Main)Hbf",
        "departure_datetime": "2016-07-09 05:16",
        "arrival_datetime": "2016-07-09 09:00",
        "price": "?"
    },
    {
        "route_name": "ICE27",
        "departure_station": "8002549",
        "dep_st_name": "Hamburg Hbf",
        "arrival_station": "8000105",
        "arr_st_name": "Frankfurt(Main)Hbf",
        "departure_datetime": "2016-07-09 05:46",
        "arrival_datetime": "2016-07-09 12:13",
        "price": "?"
    },
    ...

### Steps
1. Download [latest GFTS release](https://github.com/fredlockheed/db-fv-gtfs/releases)
2. Run API_DB_part1.py
3. Run API_DB_part2.py


### Important
Code works, but it can definitely be optimized and improved. Any contribution to make it better is more than welcome! :)


### Additional information:
Deutsche Bahn API:
* http://data.deutschebahn.com/apis/fahrplan/
* https://s3.eu-central-1.amazonaws.com/opendata-dbsiat/static/apis/fahrplan/Fpl-API-Doku-Open-Data-BETA-0_81_2.pdf

In GitHub:
* https://github.com/dbopendata/db-fahrplan-api
* https://github.com/fredlockheed/db-fv-gtfs/releases (GTFS)
