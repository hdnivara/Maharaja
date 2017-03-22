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

    LOG.debug("ADSBX query: %s", query)
    return query


def flights_str_get(print_fltr, flights):
    """ Pretty print flight data.

    Args:
        print_fltr (list): List of attributes to print.
        flights (dict): Dict of ADS-B Exchange flight data.
    """

    # Print a neat header of the attributes.
    header = ""
    for each_item in print_fltr:
        header += "{:12s}".format(each_item.upper())
    header += "\n"

    # Print the data.
    flight_data = ""
    pkeys = [FLTR_RESPS[key] for key in print_fltr]
    for each_flight in flights:
        # Extract intersted keys/values to print in to a new dict.
        flight = dict((k, each_flight[k]) for k in pkeys if k in each_flight)

        if all(key in flight for key in pkeys):
            for key in pkeys:
                if key is "To" or key is "From":
                    val = each_flight[key].encode(encoding="utf-8")[:4]
                else:
                    val = str(each_flight[key])
                flight_data += "{:12s}".format(val)
            flight_data += "\n"

    return header + flight_data

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

    # Fetch flight information.
    fltr = {}
    fltr["country"] = "United States"
    fltr["operator"] = "Alaska"
    flight_data = flights_get(fltr)
    rflights = flights_refine(FLTR_RESPS.values(), flight_data)

    # Print flight information.
    print_fltr = ["callsign", "from", "to", "type", "latitude", "longitude",
                  "regn"]
    flights = flights_str_get(print_fltr, rflights)
    print flights

if __name__ == "__main__":
    main()
