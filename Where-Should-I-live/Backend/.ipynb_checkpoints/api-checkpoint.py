"""Local demo API for the Where Should I Live? prototype."""

from flask import Flask, jsonify, render_template, request

app = Flask(
    __name__,
    template_folder="../Frontend",
    static_folder="../Frontend",
    static_url_path="/static",
)

# Illustrative monthly rents for a quick local prototype. These are not live
# market data; replace this list with a sourced dataset before making decisions.
SAMPLE_PLACES = [
    {"city": "Pittsburgh", "state": "Pennsylvania", "rent": 1050, "note": "Sample estimate"},
    {"city": "Cleveland", "state": "Ohio", "rent": 1100, "note": "Sample estimate"},
    {"city": "Tulsa", "state": "Oklahoma", "rent": 1150, "note": "Sample estimate"},
    {"city": "Kansas City", "state": "Missouri", "rent": 1250, "note": "Sample estimate"},
    {"city": "Albuquerque", "state": "New Mexico", "rent": 1300, "note": "Sample estimate"},
    {"city": "Salt Lake City", "state": "Utah", "rent": 1550, "note": "Sample estimate"},
    {"city": "Denver", "state": "Colorado", "rent": 1750, "note": "Sample estimate"},
    {"city": "Seattle", "state": "Washington", "rent": 2200, "note": "Sample estimate"},
]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/states")
def find_places():
    rent = request.args.get("max-rent", type=float)
    if rent is None or rent <= 0:
        return jsonify({"error": "Enter a maximum monthly rent greater than $0."}), 400

    matches = [place for place in SAMPLE_PLACES if place["rent"] <= rent]
    matches.sort(key=lambda place: place["rent"])
    return jsonify({"max_rent": rent, "places": matches})


if __name__ == "__main__":
    app.run(debug=True)
