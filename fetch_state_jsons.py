import json
import os
from pathlib import Path

import requests


api_key = os.environ["CENSUS_API_KEY"]
output_dir = Path("data/states")
output_dir.mkdir(parents=True, exist_ok=True)

for number in range(57):
    response = requests.get(
        "https://api.census.gov/data/2024/acs/acs5",
        params={
            "get": "NAME,B01003_001E,B19013_001E,B25064_001E",
            "for": f"state:{number:02d}",
            "key": api_key,
        },
        timeout=30,
    )

    response.raise_for_status()
    data = response.json()

    (output_dir / f"{number:02d}.json").write_text(
        json.dumps(data, indent=2) + "\n",
        encoding="utf-8",
    )
