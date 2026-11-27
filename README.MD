# Market Concentration in the U.S. Airline Industry

This is a Quarto website. The rendered site is in `docs/`. Open
`docs/index.html` to view it, or use the public hosting link.

## Data
The raw BTS T-100 Domestic Market (U.S. Carriers) data is included in
`data/raw/Archive.zip` in the submitted source zip. It is not stored in the
GitHub repository because of its size.

**To rebuild the summary tables from the included raw data**, leave
`Archive.zip` in `data/raw/` (the script reads zip files directly) and run
this from the project folder:

    python scripts/aggregate_t100.py data/raw data/processed

**If you only have the GitHub repository**, download the data from BTS,
https://www.transtats.bts.gov/ (Data Library > Aviation > Air Carrier
Statistics (Form 41 Traffic) - U.S. Carriers > T-100 Domestic Market), for
the sample years 2000, 2005, 2008, 2010, 2012, 2014, 2016, 2019, 2023, and
2025. Keep these columns: PASSENGERS, DISTANCE, UNIQUE_CARRIER, AIRLINE_ID,
UNIQUE_CARRIER_NAME, ORIGIN, ORIGIN_CITY_NAME, ORIGIN_STATE_ABR, DEST, YEAR,
MONTH, CLASS. Place the files (CSV or zip) in `data/raw/`, then run the
command above.

`data/processed/` (already included) holds the summary tables the site reads,
so rendering the site does not require the raw data.
`data/external/airports.dat` is from OpenFlights.
