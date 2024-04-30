import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Define the directory where the files are located
directory = "../data/"

# List of categories
categories = ["outcomes", "stop-and-search", "street"]

# List of months from April 2021 to December 2023
months = [f"{year}-{month:02d}" for year in range(2021, 2024) for month in range(4, 13)]

for category in categories:
    # Initialize an empty DataFrame to store the merged data
    merged_data = pd.DataFrame()

    # Loop through each month
    for month in months:
        # Construct the filename for the current month and category
        filename = f"{month}-city-of-london-{category}.csv"
        file_path = os.path.join(directory, filename)

        # Check if the file exists
        if os.path.exists(file_path):
            # Read the file and append its data to the merged_data DataFrame
            data = pd.read_csv(file_path)
            merged_data = merged_data.append(data, ignore_index=True)

    # Write the merged data to a new CSV file
    merged_file_path = os.path.join(directory, f"city-of-london-{category}-merged.csv")
    merged_data.to_csv(merged_file_path, index=False)

    # Print the first few rows of the merged DataFrame
    print(f"First few rows of {merged_file_path}:")
    print(merged_data.head())
    print()  # Add an empty line for clarity

# Load the merged DataFrame
merged_outcomes = pd.read_csv("../data/city-of-london-outcomes-merged.csv")
merged_stop_and_search = pd.read_csv("../data/city-of-london-stop-and-search-merged.csv")
merged_street = pd.read_csv("../data/city-of-london-street-merged.csv")

# Print information about each DataFrame
print("city-of-london-outcomes-merged.csv:")
print(merged_outcomes.head())
print()

print("Information about city-of-london-stop-and-search-merged.csv:")
print(merged_stop_and_search.info())
print()

print("Information about city-of-london-street-merged.csv:")
print(merged_street.info())
print()