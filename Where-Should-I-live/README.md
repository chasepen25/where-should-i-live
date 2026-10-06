# Where Should I Live?

A small Flask app you can run locally to try the rent budget flow. It uses illustrative sample rents so the demo works without an API key or network data source.

## Run it

From this folder, install the dependency and start the server:

```bash
python3 -m pip install -r requirements.txt
python3 Backend/api.py
```

Then open [http://127.0.0.1:5000](http://127.0.0.1:5000). Enter a monthly rent budget and select **Find my places**. Stop the server with `Ctrl+C`.

The city rents are illustrative values in `Backend/api.py`, not current market data or listings.
