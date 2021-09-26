### TASK ###
# Write a program that queries Covalent's API ticker endpoint. 
# Collect null address results for 60 samples at a rate of 1 sample per minute. 
# After 60 samples, display a histogram of null results. Only include currencies that had >0 null address responses.

### Author
# Kristopher Buote
# September 26, 2021

### Use python's request library to query API
import requests
import time
import matplotlib.pyplot as plt
import numpy as np
import csv
import sys

### Receive API key as user input
mykey = input("Enter Covalent API Key:")

### Try an initial connection to the API
try:
    response = requests.get('https://api.covalenthq.com/v1/pricing/tickers/',
                            auth=(mykey, ''))
# Exit program if initial connection failed.
except:
    print(f"Error in request. Proram exited. Error:{sys.exc_info()[0]}")
    exit()

### Collect the API response's error and message
json_response = response.json()
error = json_response["error"]
error_message = json_response["error_message"]

### Check if response was good (i.e. 200 response code and error is false). 
# If good, continue. Else, print error code and message.
if response.status_code == 200 and error is False:
    print(f"API Response: {response.status_code}. No error. Program continuing.")

    ### Organize API response JSON data into dictionaries
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


### Collect 60 samples, approximately 1 sample per minute
for sample in range(1, 61):

    # Query API
    response = requests.get('https://api.covalenthq.com/v1/pricing/tickers/',
                            auth=(mykey, ''))

    json_response = response.json()
    error = json_response["error"]
    error_message = json_response["error_message"]
    
    # Organize API response JSON data into dictionaries
    data = json_response["data"]
    timestamp = data["updated_at"]
    all_items = data["items"]

    #print(timestamp)
    
    ### Check if an error was thrown by the API response
    # If error message is false, continue with program. Else, skip sample.
    if error is False:

        # Collect results in a nested dictionary using the Ticker symbol as key
        # A new entry will be added for each sample. If an address is returned, it will be stored. If null is returned, it will be stored as null.
        for item in all_items:
            item_ticker = item["contract_ticker_symbol"]
            item_address = item["contract_address"]
            results[item_ticker][sample] = item_address
        
    else:
        print(f"Sample {sample} failed and skipped. API error message: {error_message}")

    # Wait 1 minute for another sample. This is usually commented out for developing.
    # time.sleep(60)

# MUST REMOVE
##
### KRIS ADDED NULL INTO RESULTS TO TEST
results["WETH"][60] = None
results["WETH"][1] = None
results["WETH"][3] = None
results["USDT"][60] = None
results["USDT"][54] = None
results["BNB"][3] = None
###
##
#

### Count the amount of null responses for each ticker across the 60 samples
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
plt.savefig('null_count_histogram.png')
plt.show()




