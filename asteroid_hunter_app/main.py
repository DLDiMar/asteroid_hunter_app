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
'''

import math, requests, json, os, sys
import pprint as pretty_print
from month_information import monthInfo
from requests.exceptions import HTTPError
from datetime import datetime, timedelta
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

def errorBlock(err):
    print(f'Other error occured: {err}')
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)

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
                for closeObjects in close_approach_data:  
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
        errorBlock(err)

# Get top 10 nearest misses to Earth (past and future)
def nearest_misses():
    try:
        # Start default value where any added value will be new closest
        closestDistanceArray = deque([math.inf] * topCount)      
        closestNeosArray = deque([None] * topCount)
        closestNeosEpoch = deque([None] * topCount)
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
                    epoch_date_close_approach = closeObjects["epoch_date_close_approach"]
                    approachAstroFloat = float(closeObjects["miss_distance"]["astronomical"])

                    # If current astronomical distance is larger than largest stored value, skip
                    if (approachAstroFloat > max(closestDistanceArray)):
                        continue
                    
                    if (approachAstroFloat < closestDistanceArray[0] and orbiting_body == "Earth" ):
                        closestNeo = loadJsonPerPage["near_earth_objects"][count]
                        closestNeo["close_approach_data"] = closeObjects
                        closestDistanceArray.appendleft(approachAstroFloat)
                        closestDistanceArray.pop()
                        closestNeosArray.appendleft(closestNeo)
                        closestNeosArray.pop()
                        closestNeosEpoch.appendleft(epoch_date_close_approach)
                        closestNeosEpoch.pop()
                        pageApiClosest = pageApi

                    # If distance is between values in sorted, current close distance array, 
                    # find where it goes and insert (JSON and distance arrays) and pop off rightmost values
                    if (approachAstroFloat > closestDistanceArray[0] and approachAstroFloat < max(closestDistanceArray) and orbiting_body == "Earth"):
                        for jdx in range(0, len(closestDistanceArray)-1):
                            if (approachAstroFloat > closestDistanceArray[jdx] and (approachAstroFloat in closestDistanceArray) and (epoch_date_close_approach in closestNeosEpoch)):
                                continue
                            if (approachAstroFloat < closestDistanceArray[jdx] and (approachAstroFloat not in closestDistanceArray) and (epoch_date_close_approach not in closestNeosEpoch)):
                                closestNeosArray.insert(jdx, closestNeo)
                                closestNeosArray.pop()
                                closestDistanceArray.insert(jdx,approachAstroFloat)
                                closestDistanceArray.pop()
                                closestNeosEpoch.appendleft(epoch_date_close_approach)
                                closestNeosEpoch.pop()

            #Output Test Block: page, closest distance, index of closest approach
            print('-------')
            print(f'Current page: {pageApi}')
            print(f'Closest astronomical distance array: {closestDistanceArray}')
            print(f'Closest NEO page: {pageApiClosest}')
            print('-------')

        json.dump(list(closestNeosArray), fileTenClosestNeo, indent = 2)
        pretty_print.pprint(closestNeosArray)

        fileTenClosestNeo.close
        print('**********')

    # Ensure no issues on API site
    except HTTPError as http_err:
        print(f'HTTP error occured: {http_err}')
    # General error handler
    except Exception as err:
        errorBlock(err)


# Get closest 10 asteroids to Earth in given month
def month_closest_approaches():
    try:
        # Writing to external JSON file for extraction
        fileClosestNeoMonth = open("closest_neo_per_month.json","w")

        # Start default value where any added value will be new closest
        closestDistanceArray = deque([math.inf] * topMonthCount) 
        closestNeosArray = deque([None] * topMonthCount)
        closestNeosEpoch = deque([None] * topMonthCount)  
        totalNeosInMonth = 0 
        monthClass = monthInfo(yearToTest, monthToTest)
        
        # Object Testing Block: Date Generation
        print('-------')
        print(f'Starting day: {monthClass.startDate}')
        print(f'Ending day: {monthClass.endDate}')
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
            element_count = int(loadJson["element_count"])
            totalNeosInMonth += element_count

            # Verify search band for API request
            print('-------')
            print(f'First day of week {int(idx) + 1}: {beginningDay}')
            print(f'Last day of week{int(idx) + 1}: {endingDay}')
            print(f'Elements in week {int(idx) + 1}: {element_count}')
            print(f'Total elements so far: {totalNeosInMonth}')
            print('-------')
            
            # Iterate through all NEO's by date
            for dateNeo in loadJson["near_earth_objects"]:
                dateCheck = dateNeo

                for count, neoChoice in enumerate(loadJson["near_earth_objects"][f'{dateCheck}']):
                    close_approach_data = neoChoice["close_approach_data"]

                    for data in close_approach_data:
                        orbiting_body = str(data["orbiting_body"])
                        epoch_date_close_approach = data["epoch_date_close_approach"]
                        approachAstroFloat = float(data["miss_distance"]["astronomical"])

                        # If distance is larger than largest value in current close distance array, skip
                        if (approachAstroFloat > max(closestDistanceArray)):
                            continue

                        if (approachAstroFloat < closestDistanceArray[0] and orbiting_body == "Earth"):
                            closeNeo = loadJson["near_earth_objects"][f'{dateCheck}'][count]
                            closeNeo["close_approach_data"] = data
                            closestNeosArray.appendleft(closeNeo)
                            closestNeosArray.pop()
                            closestDistanceArray.appendleft(approachAstroFloat)
                            closestDistanceArray.pop()
                            closestNeosEpoch.appendleft(epoch_date_close_approach)
                            closestNeosEpoch.pop()
            
                        
                        # If distance is between values in sorted, current close distance array, 
                        # find where it goes and insert (JSON and distance arrays) and pop off rightmost values
                        if (approachAstroFloat > closestDistanceArray[0] and approachAstroFloat < max(closestDistanceArray) and orbiting_body == "Earth"):
                            for jdx in range(0, len(closestDistanceArray)-1):
                                if (approachAstroFloat > closestDistanceArray[jdx] and (approachAstroFloat in closestDistanceArray) and (epoch_date_close_approach in closestNeosEpoch)):
                                    continue
                                if (approachAstroFloat < closestDistanceArray[jdx] and (approachAstroFloat not in closestDistanceArray) and (epoch_date_close_approach not in closestNeosEpoch)):
                                    closestNeosArray.insert(jdx, closeNeo)
                                    closestNeosArray.pop()
                                    closestDistanceArray.insert(jdx,approachAstroFloat)
                                    closestDistanceArray.pop()
                                    closestNeosEpoch.appendleft(epoch_date_close_approach)
                                    closestNeosEpoch.pop()
    
                #Output Test Block: page, closest distance, index of closest approach
                print('-------')
                print(f'{dateCheck}')
                print(f'Array of closest Neo distances: {closestDistanceArray}')
                print('-------')
             
        # Output JSON to file and console, then close file
        json.dump(list(closestNeosArray), fileClosestNeoMonth, indent = 2)
        fileClosestNeoMonth.close
        print('**********')
        
    # Ensure no issues on API site        
    except HTTPError as http_err:
        print(f'HTTP error occured: {http_err}')
    # General error handler
    except Exception as err:
        errorBlock(err)

# Function Calls
# Uncomment (if present) for accessing functions
asteroid_closest_approach()
nearest_misses()
month_closest_approaches()
