'''
Asteroid Hunter API Pipeline
Author: Dominic DiMarco
main.py
Rev. 1.2
Input: NASA API 
Output: .json files as per below function calls:
    asteroid_closest_approach() -> closest_neo.json
    month_closest_approaches() -> closest_neo_per_month.json
        Currently outputs element_count to console and variable: element_count
    nearest_misses() -> ten_closest_neo.json

*** Proposed Modifications on future revisions ***
-Change month_closest_approaches() to month_closest_approaches(topQty, year, month)
-Modify nearest_misses() algorithm to nearest_misses(topQty)

*** Revised Modifications on Rev 1.1 ***
-Modified nearest_misses() algorithm to both ignore repeat asteroid inserts and account for in-between values in array

*** Revised Modifications on Rev 1.2 ***
-Modify month_closest_approaches() to correctly output list of JSON objects per month of top 10

*** Revised Modifications on Rev 1.3 ***
-Revised variable convention
'''

import math, requests, json, os, sys
import pprint as pretty_print
from month_information import MonthInfo
from requests.exceptions import HTTPError
from apikey import user_api_key
from collections import deque

# Parameters
top_month_count = 10  # Count for top (qty) of asteroids in month
top_count = 10       # Top nearest misses value
month_to_test = 1     # Test integer representation of month (i.e. 1 = January)
year_to_test = 2021   # Test integer representation of year
days_per_query = 7    # Max return on Feed API
browse_api = 'https://api.nasa.gov/neo/rest/v1/neo/browse?'
feed_api = 'https://api.nasa.gov/neo/rest/v1/feed?'

# Function Definitions 

def error_block(err):
    print(f'Other error occured: {err}')
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)

# Get all asteroids and closest approach to Earth
def asteroid_closest_approach():
    try:
        closest_distance = math.inf      # Start default value where any added value will be new closest
        page_api = 0                     # API page start at 0
        page_api_closest = 0              # Page of closest NEO JSON Object

        # Writing to external JSON file for extraction
        file_closest_neo = open("closest_neo.json","w")

        # API Get request for number of pages to loop
        params = {
            'api_key':user_api_key
        }
        response = requests.get(browse_api, params=params).json() 
        response_str = json.dumps(response)
        load_json = json.loads(response_str)
        number_pages = load_json["page"]["size"]  # Extract available API pages

        # Iterate search across all API pages
        for page_api in range(0,number_pages+1):

            # API request for each page
            params = {
                'page':page_api,
                'api_key':user_api_key
            }
            response_per_page = requests.get(browse_api, params=params).json() 
            response_str_per_page = json.dumps(response_per_page)
            load_json_per_page = json.loads(response_str_per_page)

            # Iterate through all NEO's 
            for count, neo in enumerate(load_json_per_page["near_earth_objects"]):
                close_approach_data = neo["close_approach_data"]
                
                # Iterate through each NEO's close approach data
                for close_objects in close_approach_data:  
                    # Filtering parameters       
                    orbiting_body = close_objects["orbiting_body"]
                    approach_astro_float = float(close_objects["miss_distance"]["astronomical"])

                    # If NEO's closest approach is closer than previous, replace holder data and JSON output
                    if (approach_astro_float < closest_distance and orbiting_body == "Earth"):
                        closest_neo = load_json_per_page["near_earth_objects"][count]
                        closest_distance = approach_astro_float
                        page_api_closest = page_api
                        closest_neo["close_approach_data"] = close_objects

            #Output Verification Block: page, closest distance, index of closest approach
            print('-------')
            print(f'Current page: {page_api}')
            print(f'Closest astronomical distance: {closest_distance}')
            print(f'Closest NEO page: {page_api_closest}')
            print('-------')

        # Output JSON to file and console, then close file
        json.dump(closest_neo, file_closest_neo, indent = 2)
        pretty_print.pprint(closest_neo)
        file_closest_neo.close
        print('**********')

    # Ensure no issues on API site
    except HTTPError as http_err:
        print(f'HTTP error occured: {http_err}')
    # General error handler
    except Exception as err:
        error_block(err)

# Get top 10 nearest misses to Earth (past and future)
def nearest_misses():
    try:
        # Start default value where any added value will be new closest
        closest_distance_array = deque([math.inf] * top_count)      
        closest_neos_array = deque([None] * top_count)
        closest_neos_epoch = deque([None] * top_count)
        page_api = 0                     # API page start at 0
        page_api_closest = 0              # Page of closest NEO JSON Object

        # Writing to external JSON file for extraction
        file_ten_closest_neo = open("ten_closest_neo.json","w")

        # API Get request for number of pages to loop
        params = {
            'api_key':user_api_key
        }
        response = requests.get(browse_api, params=params).json() 
        response_str = json.dumps(response)      
        load_json = json.loads(response_str)
        number_pages = load_json["page"]["size"]  # Extract available API pages

        # Iterate search across all API pages
        for page_api in range(0,number_pages+1):

            # API request for each page
            params = {
                'page':page_api,
                'api_key':user_api_key
            }
            response_per_page = requests.get(browse_api, params=params).json() 
            response_str_per_page = json.dumps(response_per_page)
            load_json_per_page = json.loads(response_str_per_page)

            # Iterate through all NEO's
            for count, neo in enumerate(load_json_per_page["near_earth_objects"]):
                close_approach_data = neo["close_approach_data"]
                
                # Iterate through all NEO's close approach data
                for close_objects in close_approach_data:
                    # Filtering parameters
                    orbiting_body = close_objects["orbiting_body"]
                    epoch_date_close_approach = close_objects["epoch_date_close_approach"]
                    approach_astro_float = float(close_objects["miss_distance"]["astronomical"])

                    # If current astronomical distance is larger than largest stored value, skip
                    if (approach_astro_float > max(closest_distance_array)):
                        continue
                    
                    # If current astronomical distance is smaller than smallest stored value, append to first index
                    if (approach_astro_float < closest_distance_array[0] and orbiting_body == "Earth" ):
                        closest_neo = load_json_per_page["near_earth_objects"][count]
                        closest_neo["close_approach_data"] = close_objects
                        closest_distance_array.appendleft(approach_astro_float)
                        closest_distance_array.pop()
                        closest_neos_array.appendleft(closest_neo)
                        closest_neos_array.pop()
                        closest_neos_epoch.appendleft(epoch_date_close_approach)
                        closest_neos_epoch.pop()
                        page_api_closest = page_api

                    # If distance is between values in current close distance array, 
                    # find where it goes and insert (JSON and distance arrays) and pop off rightmost values
                    if (approach_astro_float > closest_distance_array[0] and approach_astro_float < max(closest_distance_array) and orbiting_body == "Earth"):
                        for jdx in range(0, len(closest_distance_array)-1):
                            if (approach_astro_float > closest_distance_array[jdx] and (approach_astro_float in closest_distance_array) and (epoch_date_close_approach in closest_neos_epoch)):
                                continue
                            if (approach_astro_float < closest_distance_array[jdx] and (approach_astro_float not in closest_distance_array) and (epoch_date_close_approach not in closest_neos_epoch)):
                                closest_neos_array.insert(jdx, closest_neo)
                                closest_neos_array.pop()
                                closest_distance_array.insert(jdx,approach_astro_float)
                                closest_distance_array.pop()
                                closest_neos_epoch.appendleft(epoch_date_close_approach)
                                closest_neos_epoch.pop()

            #Output Test Block: page, closest distance, index of closest approach
            print('-------')
            print(f'Current page: {page_api}')
            print(f'Closest astronomical distance array: {closest_distance_array}')
            print(f'Closest NEO page: {page_api_closest}')
            print('-------')

        json.dump(list(closest_neos_array), file_ten_closest_neo, indent = 2)
        pretty_print.pprint(closest_neos_array)

        file_ten_closest_neo.close
        print('**********')

    # Ensure no issues on API site
    except HTTPError as http_err:
        print(f'HTTP error occured: {http_err}')
    # General error handler
    except Exception as err:
        error_block(err)


# Get closest 10 asteroids to Earth in given month
def month_closest_approaches():
    try:
        # Writing to external JSON file for extraction
        file_closest_neo_month = open("closest_neo_per_month.json","w")

        # Start default value where any added value will be new closest
        closest_distance_array = deque([math.inf] * top_month_count) 
        closest_neos_array = deque([None] * top_month_count)
        closest_neos_epoch = deque([None] * top_month_count)  
        total_neos_in_month = 0 
        MonthClass = MonthInfo(year_to_test, month_to_test)
        
        # Object Testing Block: Date Generation
        print('-------')
        print(f'Starting day: {MonthClass.start_date}')
        print(f'Ending day: {MonthClass.end_date}')
        print('-------')

        # Determine number of weeks in month for iteration
        number_weeks_month = math.floor(int(MonthClass.end_day) / days_per_query)

        # Iterate search across all weeks in month
        for idx in range(0,number_weeks_month+1):
            beginning_day = (idx * days_per_query) + 1
            ending_day = (idx * days_per_query) + 7
            if ending_day > int(MonthClass.end_day):
                ending_day = int(MonthClass.end_day)
            if beginning_day > int(MonthClass.end_day):
                break

            # API Get request for each week to get API data
            params = {
                'start_date': f'{year_to_test:04d}-{month_to_test:02d}-{beginning_day:02d}',
                'end_date': f'{year_to_test:04d}-{month_to_test:02d}-{ending_day:02d}',
                'api_key':user_api_key
            }
            response = requests.get(feed_api, params=params).json() 
            response_str = json.dumps(response)
            load_json = json.loads(response_str)  

            # Output for Element Count of NEO's in month
            element_count = int(load_json["element_count"])
            total_neos_in_month += element_count

            # Verify search band for API request
            print('-------')
            print(f'First day of week {int(idx) + 1}: {beginning_day}')
            print(f'Last day of week{int(idx) + 1}: {ending_day}')
            print(f'Elements in week {int(idx) + 1}: {element_count}')
            print(f'Total elements so far: {total_neos_in_month}')
            print('-------')
            
            # Iterate through all NEO's by date
            for date_neo in load_json["near_earth_objects"]:
                date_check = date_neo

                for count, neo_choice in enumerate(load_json["near_earth_objects"][f'{date_check}']):
                    close_approach_data = neo_choice["close_approach_data"]

                    for close_objects in close_approach_data:
                        orbiting_body = str(close_objects["orbiting_body"])
                        epoch_date_close_approach = close_objects["epoch_date_close_approach"]
                        approach_astro_float = float(close_objects["miss_distance"]["astronomical"])

                        # If distance is larger than largest value in current close distance array, skip
                        if (approach_astro_float > max(closest_distance_array)):
                            continue

                        # If current astronomical distance is smaller than smallest stored value, append to first index
                        if (approach_astro_float < closest_distance_array[0] and orbiting_body == "Earth"):
                            close_neo = load_json["near_earth_objects"][f'{date_check}'][count]
                            close_neo["close_approach_data"] = close_objects
                            closest_neos_array.appendleft(close_neo)
                            closest_neos_array.pop()
                            closest_distance_array.appendleft(approach_astro_float)
                            closest_distance_array.pop()
                            closest_neos_epoch.appendleft(epoch_date_close_approach)
                            closest_neos_epoch.pop()
            
                        
                        # If distance is between values in current close distance array, 
                        # find where it goes and insert (JSON and distance arrays) and pop off rightmost values
                        if (approach_astro_float > closest_distance_array[0] and approach_astro_float < max(closest_distance_array) and orbiting_body == "Earth"):
                            for jdx in range(0, len(closest_distance_array)-1):
                                if (approach_astro_float > closest_distance_array[jdx] and (approach_astro_float in closest_distance_array) and (epoch_date_close_approach in closest_neos_epoch)):
                                    continue
                                if (approach_astro_float < closest_distance_array[jdx] and (approach_astro_float not in closest_distance_array) and (epoch_date_close_approach not in closest_neos_epoch)):
                                    closest_neos_array.insert(jdx, close_neo)
                                    closest_neos_array.pop()
                                    closest_distance_array.insert(jdx,approach_astro_float)
                                    closest_distance_array.pop()
                                    closest_neos_epoch.appendleft(epoch_date_close_approach)
                                    closest_neos_epoch.pop()
    
                #Output Test Block: page, closest distance, index of closest approach
                print('-------')
                print(f'{date_check}')
                print(f'Array of closest Neo distances: {closest_distance_array}')
                print('-------')
             
        # Output JSON to file and console, then close file
        json.dump(list(closest_neos_array), file_closest_neo_month, indent = 2)
        file_closest_neo_month.close
        print('**********')
        
    # Ensure no issues on API site        
    except HTTPError as http_err:
        print(f'HTTP error occured: {http_err}')
    # General error handler
    except Exception as err:
        error_block(err)

# Function Calls
# Uncomment (if present) for accessing functions
asteroid_closest_approach()
nearest_misses()
month_closest_approaches()
