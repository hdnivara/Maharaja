"""
ADS-B Exchange module to fetch flight information.

Applies the given set of filters (if any) and returns a neat JSON
of matching current flights (if any).
"""

import logging
import pprint
import requests

ADSBX_URL = "http://public-api.adsbexchange.com/VirtualRadar/AircraftList.json?"

FLTR_KEYS = {
    "latitude": "lat",       # latitude, equals
    "longitude": "lng",      # longitute, equals
    "airport": "fAirC",      # to/from/via airport code, contains
    "callsign": "fCallC",    # callsign, contains
    "country": "fCouC",      # country, contains
    "distance": "fDstU",     # distance, upto
    "icao": "fIcoC",         # ICAO code, contains
    "ismil": "fMilQ",        # is military?, equals
    "operator": "fOpC",      # operator, contains
    "regn": "fRegC",         # flight registration, contains
}

FLTR_RESPS = {
    "icao": "Icao",          # flights's ICAO code
    "to": "To",              # arrival airport
    "from": "From",          # departure airport
    "callsign": "Call",      # callsign
    "latitude": "Lat",       # latitude
    "longitude": "Long",     # longitude
    "type": "Type",          # aircraft ICAO type
    "mdl": "Mdl",            # aircraft model
    "man": "Man",            # aircraft manufacturer
    "operator": "Op",        # flight operator
    "regn": "Reg",           # aircraft registration
}

FLTR_MAPS = {
    "icao": "Icao",          # flights's ICAO code
    "to": "To",              # arrival airport
    "from": "From",          # departure airport
    "callsign": "Call",          # callsign
    "type": "Type",          # aircraft ICAO type
    "operator": "Op",        # flight operator
}

FLTR_HELP = {
    "latitude": "aircraft's current latitude",
    "longitude": "aircraft's current longitude",
    "airport": "arrival/departure/via ICAO airport code",
    "country": "country to which the aircraft is registered to",
    "distance": "distance in kms (up to)",
    "icao": "flight's ICAO code",
    "to": "arrival airport",
    "from": "departure airport",
    "callsign": "flight's callsign",
    "type": "aircraft's ICAO model type, e.g., A321 or B738",
    "man": "aircraft's manufacturer, e.g., Airbus or Boeing",
    "operator": "flight operator, e.g., Southwest or Delta",
    "regn": "aircraft's registration, e.g., VT-IDN or A6-EDF",
}

LOG = logging.getLogger(__name__)


def __build_query(fltr):
    query = ADSBX_URL
    for fltr_key in FLTR_KEYS.itervalues():
        if fltr_key in fltr:
            query += "%s=%s&" % (fltr_key, fltr.get(fltr_key))

    # Replace spaces and remove trailing '?' or '&'.
    query = query.replace(" ", "%20")
    if query.endswith("&") or query.endswith("?"):
        query = query[:-1]

    LOG.info("ADSBX query: %s", query)
    print query
    return query


def flights_print(flights):
    """ Pretty print flight data. """
    pkeys = ["Call", "To", "From", "Type"]

    print "{:10} {:6} {:6} {:5}".format("CALLSIGN", "FROM", "TO", "TYPE")
    for each_flight in flights:
        flight = dict((k, each_flight[k]) for k in pkeys if k in each_flight)

        if all(key in flight for key in pkeys):
            print "{:10} {:6} {:6} {:5}".format(
                flight["Call"], flight["From"][:4], flight["To"][:4],
                flight["Type"])


def flights_refine(fltr, flights):
    """Refine the ADS-B Exchange data into a smaller dataset.

    Args:
        fltr(list): List of flight attributes of interest.
        flights (dict): Raw ADS-B Exchange data of all flights.

    Returns:
        list: List of refined (by applying fltr) ADS-B Exchange flight data.
    """
    rflights = []

    for plane in flights['acList']:
        tmp = dict((key, plane[key]) for key in fltr if key in plane)
        rflights.append(tmp)

    LOG.debug("refined flights: %s", pprint.pformat(rflights))
    return rflights


def flights_get(flight_fltr):
    """Fetch flight(s) information from ADS-B Exchange. """

    # Map the incoming filter to ADS-B Exchange's format.
    fltr = dict((FLTR_KEYS[key], flight_fltr[key]) for key in
                flight_fltr.keys())
    LOG.debug("incoming flight filter: %s", pprint.pformat(fltr))

    # Form the query by applying the given filters.
    flight_data_query = __build_query(fltr)

    # Get the flight data from ADS-B Exchange.
    try:
        resp = requests.get(flight_data_query)
        if resp.status_code != 200:
            LOG.error("ADS-B Exchange returned error")
            return
    except requests.exceptions.RequestException:
        LOG.error("Fetching flight data from ADS-B Exchange failed",
                  exc_info=1)
        return

    jdats = resp.json()
    return jdats


def main():
    """Entry point if the module is used by itself."""
    log = logging.getLogger(__name__)
    format_str = "%(asctime)s %(name)-10s %(levelname)-5s %(message)s"
    logging.basicConfig(format=format_str)
    log.setLevel(logging.INFO)

    fltr = {}
    fltr["country"] = "United States"
    fltr["operator"] = "Alaska"
    flight_data = flights_get(fltr)
    rflights = flights_refine(FLTR_RESPS.values(), flight_data)
    flights_print(rflights)

if __name__ == "__main__":
    main()
