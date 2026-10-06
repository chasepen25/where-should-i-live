import json
from pathlib import Path


data_dir = Path("data/states")
states = []

for path in sorted(data_dir.glob("*.json")):
    response = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(response, list) or len(response) < 2:
        raise ValueError(f"{path} does not contain a Census API table response: {response}")

    headers, row = response[0], response[1]
    values = dict(zip(headers, row))
    try:
        population = int(values["B01003_001E"])
        median_income = int(values["B19013_001E"])
        median_rent = int(values["B25064_001E"])
    except (KeyError, TypeError, ValueError):
        # ACS can use negative sentinel values when a measure is unavailable.
        continue
    if population < 0 or median_income <= 0 or median_rent < 0:
        continue

    # Compare annual median rent with median household income; lower is more affordable.
    rent_share = median_rent * 12 / median_income
    states.append(
        {
            "name": values["NAME"],
            "population": population,
            "median_household_income_usd": median_income,
            "median_gross_rent_monthly_usd": median_rent,
            "annual_rent_share_of_median_income": rent_share,
        }
    )

if not states:
    raise FileNotFoundError(
        f"No state JSON files found in {data_dir}. Run fetch_state_jsons.py first."
    )

states.sort(key=lambda state: state["annual_rent_share_of_median_income"])
print(json.dumps({"best_affordability_match": states[0], "top_10": states[:10]}, indent=2))
