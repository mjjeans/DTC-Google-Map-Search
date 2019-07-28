# DTC-Google-Map-Search
An early version of the DTC which used live Google Map searches
<br>
<br>
This is an early attempt at creating the DTC (available in another repository) which used live Google Map API queries for driving distances and times. Current version uses pre-calculated results stored in a table.
<br><br>
This version was abandoned for two reasons:
<br>
The queries took too long. A progress bar for the queries was added beacuse users thought the app had frozen.
<br>
It was deemed that the number of queries generated per month would be too expensive based on Google's price scheme.
<br>
<br>
Clinics are 4 or 6 digit numbers. Some examples to try are 4697, 7193, 1234, 100150, 1032, 100038.
<br>
<br>
The three SQLite databases need to reside in the same directory as the Python script.
<br>
<br>
You'll need to add your own Google Maps API key to line 93 of the code
