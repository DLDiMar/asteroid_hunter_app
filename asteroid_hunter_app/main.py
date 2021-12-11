'''
Asteroid Hunter API Pipeline
Author: Dominic DiMarco
main.py
Input: NASA API 
Output: .json files as per below function calls:
    asteroid_closest_approach() -> closest_neo.json
    month_closest_approaches() -> closest_neo_per_month.json
        Currently outputs element_count to console and variable: element_count
    nearest_misses() -> ten_closest_neo.json
*** Proposed Modifications on future revisions ***
-Change month_closest_approaches() to month_closest_approaches(topQty, year, month)
-Modify month_closest_approaches() to correctly output list of JSON objects per month of top 10
-Modify nearest_misses() algorithm to nearest_misses(topQty)
-Modify nearest_misses() algorithm to both ignore repeat asteroid inserts and account for in-between values in array
'''

import math, requests, json, os, sys
import pprint as pretty_print
from month_information import monthInfo
from requests.exceptions import HTTPError
from apikey import userApiKey
from collections import deque

# Parameters

topMonthCount = 10  # Count for top (qty) of asteroids in month
topCount = 10       # Top nearest misses value
monthToTest = 1     # Test integer representation of month (i.e. 1 = January)
yearToTest = 2021   # Test integer representation of year
daysPerQuery = 7    # Max return on Feed API

browseApi = 'https://api.nasa.gov/neo/rest/v1/neo/browse?'
feedApi = 'https://api.nasa.gov/neo/rest/v1/feed?'

# Function Definitions 

'''
# Extract JSON data to get specific fields (Recursive Fetch)
# Credit for code structure inspiration and concept: Todd Birchard (Hackers and Slackers)
# Source: https://hackersandslackers.com/extract-data-from-complex-json-python/
def json_extract(jsonObject, key):
    tempArray = []
    
    # Recursive function to reach inside nested JSON objects
    def extract(jsonObject, tempArray, key):
        # Check if object is dictionary, then parse through each key-value pair
        if isinstance(jsonObject, dict):
            for k, val in jsonObject.items():
                # Check again for type of object (dictionary or list), continue extraction
                if isinstance(val, (dict, list)):
                    extract(val, tempArray, key)
                # If value is searched key, add to temporary array
                elif k == key:
                    tempArray.append(val)

        # Check if object is list, then extract into list and continue extraction
        elif isinstance(jsonObject, list):
            for item in jsonObject:
                extract(item, tempArray, key)
        return tempArray

    jsonValues = extract(jsonObject, tempArray, key)
    return jsonValues
'''


# Get all asteroids and closest approach to Earth
def asteroid_closest_approach():
    try:
        closestDistance = math.inf      # Start default value where any added value will be new closest
        pageApi = 0                     # API page start at 0
        pageApiClosest = 0              # Page of closest NEO JSON Object

        # Writing to external JSON file for extraction
        fileClosestNeo = open("closest_neo.json","w")

        # API Get request for number of pages to loop
        params = {
            'api_key':userApiKey
        }
        response = requests.get(browseApi, params=params).json() 
        responseStr = json.dumps(response)
        loadJson = json.loads(responseStr)
        numberPages = loadJson["page"]["size"]  # Extract available API pages

        # Iterate search across all API pages
        for pageApi in range(0,numberPages+1):

            # API request for each page
            params = {
                'page':pageApi,
                'api_key':userApiKey
            }
            responsePerPage = requests.get(browseApi, params=params).json() 
            responseStrPerPage = json.dumps(responsePerPage)
            loadJsonPerPage = json.loads(responseStrPerPage)

            # Iterate through all NEO's 
            for count, neo in enumerate(loadJsonPerPage["near_earth_objects"]):
                close_approach_data = neo["close_approach_data"]
                
                # Iterate through each NEO's close approach data
                for closeCount, closeObjects in enumerate(close_approach_data):  
                    # Filtering parameters       
                    orbiting_body = closeObjects["orbiting_body"]
                    approachAstroFloat = float(closeObjects["miss_distance"]["astronomical"])

                    # If NEO's closest approach is closer than previous, replace holder data and JSON output
                    if (approachAstroFloat < closestDistance and orbiting_body == "Earth"):
                        closestNeo = loadJsonPerPage["near_earth_objects"][count]
                        closestDistance = approachAstroFloat
                        pageApiClosest = pageApi
                        closestNeo["close_approach_data"] = closeObjects

            
            #Output Verification Block: page, closest distance, index of closest approach
            print('-------')
            print(f'Current page: {pageApi}')
            print(f'Closest astronomical distance: {closestDistance}')
            print(f'Closest NEO page: {pageApiClosest}')
            print('-------')

        # Output JSON to file and console, then close file
        json.dump(closestNeo, fileClosestNeo, indent = 2)
        pretty_print.pprint(closestNeo)
        fileClosestNeo.close
        print('**********')

    # Ensure no issues on API site
    except HTTPError as http_err:
        print(f'HTTP error occured: {http_err}')
    # General error handler
    except Exception as err:
        print(f'Other error occured: {err}')
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

# Get top 10 nearest misses to Earth (past and future)
# *** Note on this algorithm: ***
# -Storing algorithm in ascending distance not accurate, 
# propose sort() function (O(nlong(n) operation))
def nearest_misses():
    try:
        # Start default value where any added value will be new closest
        closestDistanceArr = deque([math.inf] * topCount)      
        # Initial closest NEO's array
        closestNeoArr = deque([None] * topCount)
        pageApi = 0                     # API page start at 0
        pageApiClosest = 0              # Page of closest NEO JSON Object

        # Writing to external JSON file for extraction
        fileTenClosestNeo = open("ten_closest_neo.json","w")

        # API Get request for number of pages to loop
        params = {
            'api_key':userApiKey
        }
        response = requests.get(browseApi, params=params).json() 
        responseStr = json.dumps(response)
        loadJson = json.loads(responseStr)
        numberPages = loadJson["page"]["size"]  # Extract available API pages

        # Iterate search across all API pages
        for pageApi in range(0,numberPages+1):

            # API request for each page
            params = {
                'page':pageApi,
                'api_key':userApiKey
            }
            responsePerPage = requests.get(browseApi, params=params).json() 
            responseStrPerPage = json.dumps(responsePerPage)
            loadJsonPerPage = json.loads(responseStrPerPage)

            # Iterate through all NEO's
            for count, neo in enumerate(loadJsonPerPage["near_earth_objects"]):
                close_approach_data = neo["close_approach_data"]
                
                # Iterate through all NEO's close approach data
                for closeObjects in close_approach_data:
                    # Filtering parameters
                    orbiting_body = closeObjects["orbiting_body"]
                    approachAstroFloat = float(closeObjects["miss_distance"]["astronomical"])

                    # If current astronomical distance is larger than largest stored value, skip
                    if (approachAstroFloat > max(closestDistanceArr)):
                        continue
                    
                    if (approachAstroFloat < closestDistanceArr[0] and orbiting_body == "Earth"):
                        closestNeo = loadJsonPerPage["near_earth_objects"][count]
                        closestNeo["close_approach_data"] = closeObjects
                        closestDistanceArr.appendleft(approachAstroFloat)
                        closestDistanceArr.pop()
                        closestNeoArr.appendleft(closestNeo)
                        closestNeoArr.pop()
                        pageApiClosest = pageApi

                    '''
                    # *** Requires fix (repeating asteroid insert) ***
                    # If distance is between values in sorted, current close distance array, 
                    # find where it goes and insert (JSON and distance arrays) and pop off rightmost values
                    if (approachAstroFloat > closestDistanceArr[0] and approachAstroFloat < max(closestDistanceArr) and orbiting_body == "Earth"):
                        for jdx in range(0, len(closestDistanceArr)-1):
                            if approachAstroFloat > closestDistanceArr[jdx]:
                                continue
                            if approachAstroFloat < closestDistanceArr[jdx]:
                                closestNeoArr.insert(jdx, closestNeo)
                                closestNeoArr.pop()
                                closestDistanceArr.insert(jdx,approachAstroFloat)
                                closestDistanceArr.pop()
                    '''
            
            #Output Test Block: page, closest distance, index of closest approach
            print('-------')
            print(f'Current page: {pageApi}')
            print(f'Closest astronomical distance array: {closestDistanceArr}')
            print(f'Closest NEO page: {pageApiClosest}')
            print('-------')
            

        json.dump(list(closestNeoArr), fileTenClosestNeo, indent = 2)
        pretty_print.pprint(closestNeoArr)

        fileTenClosestNeo.close
        print('**********')
    # Ensure no issues on API site
    except HTTPError as http_err:
        print(f'HTTP error occured: {http_err}')
    # General error handler
    except Exception as err:
        print(f'Other error occured: {err}')
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)


# Get closest 10 asteroids to Earth in given month
# Current issues: 
# -Algorithm does not reach level below "near_earth_objects" in nested JSON data
# -Storing algorithm in ascending distance not accurate, propose sort() function (O(nlong(n) operation))
def month_closest_approaches():
    try:
        # Writing to external JSON file for extraction
        fileClosestNeoMonth = open("closest_neo_per_month.json","w")

        monthClass = monthInfo(yearToTest, monthToTest)

        # Start default value where any added value will be new closest
        closestDistanceArray = deque([math.inf] * topMonthCount) 
        closestNeosArray = deque([None] * topMonthCount)  
        totalNeosInMonth = 0 
        
        # Object Testing Block: Date Generation
        print('-------')
        print(f'Starting day: {monthClass.startDate}')
        print(f'Ending day: {monthClass.endDate}')
        print(f'Initial Closest Distance Top 10 (Astronomical Dist): {closestDistanceArray}')
        print(f'Initial CLosest NEO JSON Output: {closestNeosArray}')
        print('-------')

        # Determine number of weeks in month for iteration
        numberWeeksMonth = math.floor(int(monthClass.endDay) / daysPerQuery)

        # Iterate search across all weeks in month
        for idx in range(0,numberWeeksMonth+1):
            beginningDay = (idx * daysPerQuery) + 1
            endingDay = (idx * daysPerQuery) + 7
            if endingDay > int(monthClass.endDay):
                endingDay = int(monthClass.endDay)
            if beginningDay > int(monthClass.endDay):
                break

            # Verify search band for API request
            print('-------')
            print(f'First day of week {int(idx) + 1}: {beginningDay}')
            print(f'Last day of week{int(idx) + 1}: {endingDay}')
            print('-------')

            # API Get request for each week to get API data
            params = {
                'start_date': f'{yearToTest:04d}-{monthToTest:02d}-{beginningDay:02d}',
                'end_date': f'{yearToTest:04d}-{monthToTest:02d}-{endingDay:02d}',
                'api_key':userApiKey
            }
            response = requests.get(feedApi, params=params).json() 
            responseStr = json.dumps(response)
            loadJson = json.loads(responseStr)  

            # Output for Element Count of NEO's in month
            element_count = loadJson["element_count"]
            totalNeosInMonth += int(element_count)

            # Console verification of Element counts
            print('-------')
            print(f'Elements in week {int(idx) + 1}: {element_count}')
            print(f'Total elements so far: {totalNeosInMonth}')
            print('-------')

            # Iterate through all NEO's 
            for count, neo in enumerate(loadJson["near_earth_objects"]):
                # *** Can't seem to get past this level on the nested JSON: ***
                # Appears to go into a list of NEO's of each date, but when trying
                # to access this, it believes date needs to be an int and not string
                print(neo[:])
                close_approach_data = neo["close_approach_data"]
                
                # Iterate through each NEO's close approach data
                for closeCount, closeObjects in enumerate(close_approach_data): 
                    orbiting_body = closeObjects["orbiting_body"]
                    print(f'Orbiting Body: {orbiting_body}')
                    approachAstroFloat = float(closeObjects["miss_distance"]["astronomical"])
                    
                    # If distance is larger than largest value in current close distance array, skip
                    if (approachAstroFloat > max(closestDistanceArray)):
                        continue
                    
                    # If distance is smaller than smallest value in sorted, current close distance array, 
                    # insert value from left of queue and pop off the rightmost (JSON and distance arrays)
                    if (approachAstroFloat < closestDistanceArray[0] and orbiting_body == "Earth"):
                        closeNeo = loadJson["near_earth_objects"][count]
                        closeNeo["close_approach_data"] = closeObjects
                        closestNeosArray.appendleft(closeNeo)
                        closestNeosArray.pop()
                        closestDistanceArray.appendleft(approachAstroFloat)
                        closestDistanceArray.pop()
                    
                    ''''
                    # *** Requires fix (repeating asteroid insert) ***
                    # If distance is between values in sorted, current close distance array, 
                    # find where it goes and insert (JSON and distance arrays) and pop off rightmost values
                    if (approachAstroFloat > closestDistanceArray[0] and approachAstroFloat < max(closestDistanceArray) and orbiting_body == "Earth"):
                        for jdx in range(0, len(closestDistanceArray)):
                            if approachAstroFloat > closestDistanceArray[jdx]:
                                continue
                            if approachAstroFloat < closestDistanceArray[jdx]:
                                closestNeosArray.insert(jdx, closeNeo)
                                closestNeosArray.pop()
                                closestDistanceArray.insert(jdx, approachAstroFloat)
                                closestDistanceArray.pop()
                    '''

            #Output Test Block: page, closest distance, index of closest approach
            print('-------')
            print(f'Array of closest Neo distances: {closestNeosArray}')
            print('-------')
                
        # Output JSON to file and console, then close file
        json.dump(closestNeosArray, fileClosestNeoMonth, indent = 2)
        pretty_print.pprint(closeNeo)
        fileClosestNeoMonth.close
        print('**********')

    # Ensure no issues on API site        
    except HTTPError as http_err:
        print(f'HTTP error occured: {http_err}')
    # General error handler
    except Exception as err:
        print(f'Other error occured: {err}')
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

# Function Calls
# Uncomment (if present) for accessing functions

asteroid_closest_approach()
nearest_misses()
month_closest_approaches()