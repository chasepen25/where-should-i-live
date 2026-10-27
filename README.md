# Where Should I Live?

A small Flask app you can run locally to try the rent budget flow. It uses illustrative sample rents so the demo works without an API key or network data source.

## Run it

From this folder, install the dependency and start the server:

```bash
python3 -m pip install -r requirements.txt
python3 Backend/api.py
```

Then open [http://127.0.0.1:5000](http://127.0.0.1:5000). Choose whether you plan to rent or buy, enter a housing budget and household income, then select **Find my places**. The demo compares those answers with the 2024 ACS estimates in `state_housing_data.csv`. Stop the server with `Ctrl+C`.

The city rents are illustrative values in `Backend/api.py`, not current market data or listings.

## Fetch Census state data

The state data fetcher uses the 2024 ACS 5-year Census API. Request a free API key from the [U.S. Census Bureau](https://api.census.gov/data/key_signup.html), then:

1. Install the project dependencies with `python3 -m pip install -r requirements.txt`.
2. Copy `.env.example` to `.env`.
3. Replace the example value in `.env` with your Census API key. Keep `.env` private; it is ignored by Git.
4. Run `python3 fetch_state_jsons.py` to fetch each valid state FIPS code and write the raw responses under `data/states/`.
5. Run `python3 recommend_state.py` to print the affordability ranking from those files.
