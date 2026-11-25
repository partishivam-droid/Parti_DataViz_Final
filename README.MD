# Market Concentration in the U.S. Airline Industry

Quarto website. Rendered site is in `docs/`; open `docs/index.html`.

## Data
The raw data is not included because of its size.

1. Download BTS T-100 Domestic Market (U.S. Carriers) from
   https://www.transtats.bts.gov/ (Data Library > Aviation > Air Carrier
   Statistics (Form 41 Traffic) - U.S. Carriers > T-100 Domestic Market)
   for the sample years: 2000, 2005, 2008, 2010, 2012, 2014, 2016, 2019,
   2023, 2025. Keep these columns: PASSENGERS, DISTANCE, UNIQUE_CARRIER,
   AIRLINE_ID, UNIQUE_CARRIER_NAME, ORIGIN, ORIGIN_CITY_NAME,
   ORIGIN_STATE_ABR, DEST, YEAR, MONTH, CLASS.
2. Place the files (CSV or zip) in `data/raw/`.
3. Run `python scripts/aggregate_t100.py data/raw data/processed`.

`data/processed/` (already included) holds the summary tables the site
reads, and `data/external/airports.dat` is from OpenFlights.