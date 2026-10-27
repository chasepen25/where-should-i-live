"""Run the local housing recommendation demo."""

import csv
from pathlib import Path

from flask import Flask, jsonify, render_template, request


ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "Frontend"
CSV_PATH = ROOT_DIR / "state_housing_data.csv"

app = Flask(
    __name__,
    template_folder=str(FRONTEND_DIR),
    static_folder=str(FRONTEND_DIR),
    static_url_path="/static",
)


def load_housing_data():
    with CSV_PATH.open(newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/states")
def recommend_states():
    plan = request.args.get("housing-plan", "rent")
    if plan not in {"rent", "buy"}:
        return jsonify(error="Choose whether you plan to rent or buy."), 400

    try:
        budget = float(request.args.get("housing-budget", ""))
        income = float(request.args.get("household-income", ""))
    except (TypeError, ValueError):
        return jsonify(error="Enter a valid housing budget and household income."), 400
    if budget <= 0 or income <= 0:
        return jsonify(error="Housing budget and household income must be greater than $0."), 400

    try:
        rows = load_housing_data()
    except OSError:
        app.logger.exception("Could not read the state housing data CSV")
        return jsonify(error="Housing data file not found."), 500

    if plan == "rent":
        field = "median_monthly_rent"
        affordable_limit = min(budget, income * 0.30 / 12)
        price_label = "median monthly rent"
    else:
        field = "median_home_value"
        affordable_limit = min(budget, income * 3)
        price_label = "median home value"

    places = []
    for row in rows:
        try:
            amount = float(row[field])
            median_income = float(row["median_household_income"])
        except (KeyError, TypeError, ValueError):
            continue
        if amount <= 0 or median_income <= 0 or amount > affordable_limit:
            continue
        places.append(
            {
                "city": row["location"],
                "state": "Statewide estimate",
                "rent": round(amount),
                "note": f"2024 ACS 5-year {price_label} estimate",
            }
        )

    places.sort(key=lambda place: (place["rent"], place["city"]))
    return jsonify(
        {
            "housing_plan": plan,
            "housing_budget": budget,
            "household_income": income,
            "places": places,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
