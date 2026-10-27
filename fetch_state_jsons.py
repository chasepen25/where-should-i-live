import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()
api_key = os.environ.get("CENSUS_API_KEY")
if not api_key:
    raise SystemExit(
        "CENSUS_API_KEY is missing. Copy .env.example to .env and add your Census API key."
    )

output_dir = Path("data/states")
output_dir.mkdir(parents=True, exist_ok=True)

# Census state FIPS codes within 00–56. Skip 00 and reserved or obsolete codes.
state_codes = [
    number
    for number in range(57)
    if number not in {0, 3, 7, 14, 43, 52}
]

for number in state_codes:
    try:
        response = requests.get(
            "https://api.census.gov/data/2024/acs/acs5",
            params={
                "get": (
                    "NAME,B01003_001E,B19013_001E,B25064_001E,"
                    "B15003_001E,B15003_027E,B15003_028E,B15003_029E,B15003_030E,"
                    "B23025_001E,B23025_004E"
                ),
                "for": f"state:{number:02d}",
                "key": api_key,
            },
            timeout=30,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        status = exc.response.status_code if exc.response is not None else "network error"
        raise SystemExit(
            f"Census request failed for state:{number:02d} ({status}). "
            "Check the API key and connection."
        ) from None

    data = response.json()

    (output_dir / f"{number:02d}.json").write_text(
        json.dumps(data, indent=2) + "\n",
        encoding="utf-8",
    )
