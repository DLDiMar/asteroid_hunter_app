import json, math, requests
from asteroid_hunter_app.month_information import monthInfo
from asteroid_hunter_app import __version__, main, apikey


def test_version():
    assert __version__ == '0.1.0'

def test_near_misses():
    # Test JSON type output of functions
    assert type(main.nearest_misses()) == json
    assert type(main.asteroid_closest_approach()) == json
    assert type(main.month_closest_approaches()) == json

    # Test HTTP Request statuses of API's
    params = {
        'api_key':apikey.userApiKey
    }
    assert (requests.get(main.browseApi, params=params)).status_code ==  200
    assert (requests.get(main.feedApi, params=params)).status_code == 200

    responseStr = json.dumps(requests.get(main.browseApi, params=params).json())
    loadJson = json.loads(responseStr)
    numberPages = loadJson["page"]["size"]  
    assert (numberPages) == 20

    # Test Output JSON file for asteroid_closest_approach()
    fileOpen1 = open('closest_neo.json') 
    loadJsonOutput1 = json.load(fileOpen1)
    assert(loadJsonOutput1["id"]) == "2099942"

    # Test Output JSON file for nearest_misses()
    fileOpen2 = open('ten_closest_neo.json')
    loadJsonOutput2 = json.load(fileOpen2)
    assert(loadJsonOutput2[0]["id"]) == "2099942"

    # Test Month Information Class parameters and methods
    monthTest1 = monthInfo(2021, 1)
    assert (monthTest1.startDate) == 1
    assert (monthTest1.endDate) == 31
    assert (monthTest1.daysInMonth()) == 31
    numberWeeksMonth1 = math.floor(int(monthTest1.endDay) / main.daysPerQuery)
    assert (numberWeeksMonth1) == 5

    monthTest2 = monthInfo(2021, 2)
    assert (monthTest2.endDate) == 28
    assert (monthTest2.daysInMonth()) == 28
    numberWeeksMonth2 = math.floor(int(monthTest2.endDay) / main.daysPerQuery)
    assert (numberWeeksMonth2) == 4

    monthTest3 = monthInfo(2020, 2)
    assert (monthTest3.endDate) == 29
    assert (monthTest3.daysInMonth()) == 29
    numberWeeksMonth3 = math.floor(int(monthTest3.endDay) / main.daysPerQuery)
    assert (numberWeeksMonth3) == 5