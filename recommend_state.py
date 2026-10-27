"""Recommend states using affordability, education, and employment indicators."""

import argparse
import json
import math
from pathlib import Path


DEFAULT_DATA_DIR = Path(__file__).resolve().parent / "data" / "states"
EDUCATION_FIELDS = ("B15003_027E", "B15003_028E", "B15003_029E", "B15003_030E")


def load_states(data_dir=DEFAULT_DATA_DIR):
    """Load usable state estimates from Census ACS JSON files."""
    data_dir = Path(data_dir)
    states = []

    for path in sorted(data_dir.glob("*.json")):
        response = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(response, list) or len(response) < 2:
            raise ValueError(f"{path} does not contain a Census API table response")

        headers, row = response[0], response[1]
        values = dict(zip(headers, row))
        try:
            population = int(values["B01003_001E"])
            median_income = int(values["B19013_001E"])
            median_rent = int(values["B25064_001E"])
            adults_25_plus = int(values["B15003_001E"])
            bachelors_or_higher = sum(int(values[key]) for key in EDUCATION_FIELDS)
            population_16_plus = int(values["B23025_001E"])
            employed = int(values["B23025_004E"])
        except (KeyError, TypeError, ValueError):
            # Census uses negative sentinel values when an estimate is unavailable.
            continue
        if (
            population <= 0
            or median_income <= 0
            or median_rent < 0
            or adults_25_plus <= 0
            or population_16_plus <= 0
            or min(bachelors_or_higher, employed) < 0
        ):
            continue

        rent_share = median_rent * 12 / median_income
        states.append(
            {
                "name": values["NAME"],
                "population": population,
                "median_household_income_usd": median_income,
                "median_gross_rent_monthly_usd": median_rent,
                "annual_rent_share_of_median_income": rent_share,
                "bachelors_or_higher_share_age_25_plus": bachelors_or_higher / adults_25_plus,
                "employment_to_population_ratio_age_16_plus": employed / population_16_plus,
            }
        )

    if not states:
        raise FileNotFoundError(
            f"No usable state JSON files found in {data_dir}. Run fetch_state_jsons.py first."
        )
    return states


def _add_recommendation_scores(states):
    """Add equal-weight percentile scores; larger values indicate a better fit."""
    metrics = (
        ("annual_rent_share_of_median_income", False),
        ("bachelors_or_higher_share_age_25_plus", True),
        ("employment_to_population_ratio_age_16_plus", True),
    )
    for state in states:
        state["recommendation_score"] = 0.0

    # Percentile ranks keep unlike measures on the same scale. Tied values share
    # the average rank. Affordability is better when its rent share is lower.
    for field, higher_is_better in metrics:
        ordered = sorted(states, key=lambda state: state[field], reverse=higher_is_better)
        ranks = {}
        index = 0
        while index < len(ordered):
            end = index + 1
            while end < len(ordered) and ordered[end][field] == ordered[index][field]:
                end += 1
            percentile = 100 * (1 - ((index + end - 1) / 2) / max(len(ordered) - 1, 1))
            for tied in ordered[index:end]:
                ranks[tied["name"]] = percentile
            index = end
        for state in states:
            state["recommendation_score"] += ranks[state["name"]] / len(metrics)

    return states


def recommend_states(housing_budget=None, data_dir=DEFAULT_DATA_DIR):
    """Return states ranked by affordability, adult education, and employment."""
    states = _add_recommendation_scores(load_states(data_dir))
    if housing_budget is not None:
        if not math.isfinite(housing_budget) or housing_budget < 0:
            raise ValueError("housing_budget must be a finite amount of zero or greater")
        states = [
            state for state in states
            if state["median_gross_rent_monthly_usd"] <= housing_budget
        ]
    return sorted(states, key=lambda state: (-state["recommendation_score"], state["name"]))


def main():
    parser = argparse.ArgumentParser(
        description="Recommend U.S. states using affordability, education, and employment."
    )
    parser.add_argument(
        "--housing-budget",
        type=float,
        help="Optional maximum monthly budget, compared with state median gross rent.",
    )
    parser.add_argument("--limit", type=int, default=10, help="Number of recommendations to show.")
    args = parser.parse_args()

    if args.limit < 1:
        parser.error("--limit must be at least 1")
    try:
        states = recommend_states(args.housing_budget)
    except (ValueError, FileNotFoundError) as error:
        parser.error(str(error))

    factors = {
        "affordability": "lower annual median rent as a share of median household income is better",
        "schools_proxy": "higher share of adults age 25+ with a bachelor's degree or higher is better",
        "jobs": "higher employed share of the population age 16+ is better",
        "scoring": "equal-weight average of state percentile ranks across all three factors",
    }
    print(
        json.dumps(
            {
                "monthly_housing_budget_usd": args.housing_budget,
                "factors": factors,
                "recommendations": states[: args.limit],
                "matching_state_count": len(states),
                "message": None if states else "No states match the supplied housing budget.",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
