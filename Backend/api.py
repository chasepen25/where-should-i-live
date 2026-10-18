
import os
import requests
import pandas as pd

API_KEY = os.environ["CENSUS_API_KEY"]

BASE_URL = "https://api.census.gov/data/2024/acs/acs5/profile"
VARIABLES_URL = BASE_URL + "/variables.json"

# 1. Get the catalog of available variables
response = requests.get(
    VARIABLES_URL,
    timeout=30
)
response.raise_for_status()

catalog = response.json()["variables"]

catalog_df = pd.DataFrame([
    {
        "variable_code": code,
        "description": details.get("label", ""),
        "concept": details.get("concept", ""),
        "group": details.get("group", "")
    }
    for code, details in catalog.items()
])

# Keep estimate and percentage-estimate columns.
# Exclude margins of error and annotation fields.
variables = sorted(
    code for code in catalog
    if code.startswith("DP")
    and code.endswith("E")
    and not code.endswith("EA")
)

# Save descriptions for every selected variable
catalog_df = catalog_df[
    catalog_df["variable_code"].isin(variables)
]
catalog_df.to_csv(
    "census_variable_descriptions.csv",
    index=False
)

# 2. Download data in batches
# NAME + state + 40 variables stays below the API limit
chunks = [
    variables[i:i + 40]
    for i in range(0, len(variables), 40)
]

combined = None

for i, chunk in enumerate(chunks, start=1):
    params = {
        "get": ",".join(["NAME"] + chunk),
        "for": "state:*",
        "key": API_KEY
    }

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=60
    )
    response.raise_for_status()

    result = response.json()
    batch_df = pd.DataFrame(
        result[1:],
        columns=result[0]
    )

    if combined is None:
        combined = batch_df
    else:
        new_columns = [
            col for col in batch_df.columns
            if col not in ["NAME", "state"]
        ]
        combined = combined.merge(
            batch_df[["state"] + new_columns],
            on="state",
            how="left"
        )

    print(f"Downloaded batch {i} of {len(chunks)}")

# 3. Convert estimates to numbers
for col in combined.columns:
    if col not in ["NAME", "state"]:
        combined[col] = pd.to_numeric(
            combined[col],
            errors="coerce"
        )

combined = combined.rename(
    columns={"NAME": "location"}
)

combined.to_csv(
    "state_community_data.csv",
    index=False
)

print(f"\nLocations: {len(combined)}")
print(f"Data columns: {len(combined.columns)}")
print("Saved state_community_data.csv")
print("Saved census_variable_descriptions.csv")
