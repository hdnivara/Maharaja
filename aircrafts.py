"""Fetch the aircrafts flying above the given latitude and longitude. """

import json
import pprint
import requests

URL = "http://public-api.adsbexchange.com/VirtualRadar/AircraftList.json?"
LAT = "37.3639"
LNG = "-121.9289"
COUNTRY = "United States"
DISTANCE = 16

AIRLINES = ["Alaska", "American", "Delta", "Southwest", "Spirit", "United"]

def query_get(fltr):
    fltr_keys = ["lat", "lng", "fCouC", "fDstU"]

    query = URL
    for key in fltr_keys:
        if key in fltr:
            query += "%s=%s&" % (key, fltr.get(key))
            print query

    # Replace spaces and remove trailing ? or &.
    query = query.replace(" ", "%20")
    if query.endswith("&") or query.endswith("?"):
        query = query[:-1]

    return query

def flights_get():

    # Filter the flights that we are interested in.
    fltr = {}
    fltr['lat'] = LAT
    fltr['lng'] = LNG
    fltr['fDstL'] = 0
    fltr['fDstU'] = DISTANCE
    fltr['fCouC'] = COUNTRY

    flight_data_query = query_get(fltr)
    print flight_data_query

    # Get the data from ADS-B Exchange. These guys rock!
    resp = requests.get(flight_data_query)
    if resp.status_code != 200:
        print "Oops!"
        exit(0)

    jdats = resp.json()
    pprint.pprint(jdats)

if "__main__" == __name__:
    flights_get()

