# db-legs
### Aim:
Create a clear and simple output of legs bewteen two cities from the data available in Deutsche Bahn API.

### Instructions:
Code is split in 3 files / parts:
* Part 1: Creates a table called 'stations' (SQLite) with all stations available in DB API
* Part 2: Obtains all legs given a specific date and time. Two additional tables (SQLite) are created. One called 'legs' registers all the legs, and another one called 'errors' register all the errors during the import and parsing. Note that in the tests performed this takes almost 1 hour and around 70.000 rows are obtained.
* Part 3: From table 'legs' output JSON with all legs between two stations.

### Important
Code works, but it can definitely be optimized and improved. Any contribution to make it better is more than welcome! :)


### Additional information:
Deutsche Bahn API:
* http://data.deutschebahn.com/apis/fahrplan/

In GitHub:
* https://github.com/dbopendata/db-fahrplan-api
