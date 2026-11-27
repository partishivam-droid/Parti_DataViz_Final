# Market Concentration in the U.S. Airline Industry

This is a Quarto website. 
The rendered site is in `docs/`. You can open `docs/index.html` to view it, or use the public hosting link.

## Data
The raw BTS T-100 data is included in `data/raw/Archive.zip` (about 58 MB).
It contains the T-100 Domestic Market (U.S. Carriers) files for the sample
years 2000, 2005, 2008, 2010, 2012, 2014, 2016, 2019, 2023, and 2025.

To rebuild the summary tables from the raw data, leave `Archive.zip` in
`data/raw/` (the script reads it directly) and run this from the project
folder:

    python scripts/aggregate_t100.py data/raw data/processed

The source is BTS, https://www.transtats.bts.gov/ (Data Library > Aviation >
Air Carrier Statistics (Form 41 Traffic) - U.S. Carriers > T-100 Domestic
Market).

`data/processed/` (already included) holds the summary tables the site reads, so rendering the site does not require the raw data. `data/external/airports.dat` is from OpenFlights.