### TASK ###
# Write a program that queries Covalent's API ticker endpoint. 
# Collect null contract address results for 60 samples at a rate of 1 sample per minute. 
# After 60 samples, display a histogram of null results. Only include currencies that have >0 null address responses.

### AUTHOR ###
# Kristopher Buote
# September 26, 2021

### Use python's requests library to query API
import requests
import time
import matplotlib.pyplot as plt
import numpy as np
import csv
import sys

### SET UP ###
# Test connection to the Covalent API with error handling. 
# Organize the response data into dictionaries.
# Create a dictionary to store the contract addresses from the API response.
# This program uses the Ticker to associate with sample responses. 

### Receive API key as user input
mykey = input("Enter Covalent API Key:")

### Try an initial connection to the API
try:
    response = requests.get('https://api.covalenthq.com/v1/pricing/tickers/',
                            auth=(mykey, ''))

# Exit program if initial connection failed.
except:
    print(f"Connection error. Program exited. Error:{sys.exc_info()[0]}")
    exit()

### Collect the API's response error and message
json_response = response.json()
error = json_response["error"]
error_message = json_response["error_message"]

### Check if response was good (i.e. 200 response code and error is false). 
# If good, continue. Else, print error code and message.
if response.status_code == 200 and error is False:
    print(f"API Response: {response.status_code}. No error. Program continuing.")

    ### Organize API response JSON data
    data = json_response["data"]
    timestamp = data["updated_at"]
    items = data["items"]
    
    ### Create a dictionary using the currency Ticker symbols to store results  
    # *** This program assumes there will be no errors returned by the contract_ticker_symbol. It also assumes the same ticker symbols will be returned every sample***
    results = {}

    # Collect the ticker symbols and store them in results
    for item in items:
        ticker_symbol = item["contract_ticker_symbol"]
        results[ticker_symbol] = {}

else: 
    print(f"API Response Code: {response.status_code} \nAPI Error Message: {error_message}\nProgram failed and exited.")
    exit()


### DATA COLLECTION ###
# Collect 60 samples, approximately 1 sample per minute
# The results are stored in a nested dictionary using the Ticker and sample count as keys.
# e.g. {'Ticker1': {1: 'abcd', 2: null, ..., 60: 'abcd'}, 'Ticker2': {1: 'efg', 2: 'efg', ..., 60: null}}

for sample in range(1, 61):

    # Query API
    response = requests.get('https://api.covalenthq.com/v1/pricing/tickers/',
                            auth=(mykey, ''))

    json_response = response.json()
    error = json_response["error"]
    error_message = json_response["error_message"]
    
    # Organize API response JSON data
    data = json_response["data"]
    timestamp = data["updated_at"]
    all_items = data["items"]
    
    ### Check if an error was thrown by the API response
    # If error message is false, continue with program. Else, skip sample.
    if error is False:

        # Collect results in a nested dictionary using the Ticker symbol as key
        # A new entry will be added for each sample. If an address is returned, it will be stored. If null is returned, it will be stored as null.
        for item in all_items:
            item_ticker = item["contract_ticker_symbol"]
            item_address = item["contract_address"]
            results[item_ticker][sample] = item_address
            
        print(f"Sample {sample} collected.")
        
    else:
        print(f"Sample {sample} failed and skipped. API error message: {error_message}")

    # Wait 1 minute for another sample. This is usually commented out for developing.
    time.sleep(60)

### DATA ANALYSIS ###
# Count the amount of null responses for each ticker across the 60 samples
# Note that None is the variable for null in python

# Create a new dictionary to store the null count
ticker_null_count = {}

# Count the number of null address responses for each ticker
for ticker, samples in results.items():
    null_count = sum(value == None for value in samples.values())
    ticker_null_count[ticker] = null_count

# Exclude the tickers with a zero null count
ticker_null_count_non_zero = {key: value for key, value in ticker_null_count.items() if value != 0}

# Sort the dictionary in ascending order
ticker_null_count_ordered = {key: value for key, value in sorted(ticker_null_count_non_zero.items(), key=lambda item: item[1])}

### DATA PRESENTATION AND SAVING ###
### Save the null count data to a csv file
with open('null_count.csv', 'w') as csv_file:  
    writer = csv.writer(csv_file)
    for key, value in ticker_null_count_non_zero.items():
       writer.writerow([key, value])

### Create a histogram for the null counts in ascending order. Save the figure as a png file.
plt.bar(ticker_null_count_ordered.keys(), ticker_null_count_ordered.values(), width=1.0, color='g')
plt.title("Null Address Count over 60 samples")
plt.xlabel("Currency Ticker")
plt.ylabel("Null Address Count")

# Save the figure
plt.savefig('null_count_histogram.png')
plt.show()

print("Program complete.")




