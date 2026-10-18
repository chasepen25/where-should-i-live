import flask as f
import pandas as pd
import os
import requests


API_key = "97bda4c6b80cd9f9c75a1db2927b64ae53d6391a"

url = "https://api.census.gov/data/2024/acs/acs5"

params = {
    "get": "NAME,B25064_001E,B25077_001E,B19013_001E",
    "for": "state:*",
    "key": API_key
}

# Request the data
response = requests.get(url, params=params, timeout=30)
response.raise_for_status()

# Convert the response into a pandas DataFrame
data = response.json()
df = pd.DataFrame(data[1:], columns=data[0])

# Give the columns readable names
df = df.rename(columns={
    "NAME": "location",
    "B25064_001E": "median_monthly_rent",
    "B25077_001E": "median_home_value",
    "B19013_001E": "median_household_income"
})

# Convert numeric columns to numbers
columns = [
    "median_monthly_rent",
    "median_home_value",
    "median_household_income"
]

for column in columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

# Display the results
print(df.head(100))

# Save the data to a CSV file
df.to_csv("state_housing_data.csv", index=False)

