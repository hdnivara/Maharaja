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
    "fk_latitute": "lat",       # latitude, equals
    "fk_longitude": "lng",      # longitute, equals
    "fk_airport": "fAirC",      # to/from/via airport code, contains
    "fk_callsign": "fCallC",    # callsign, contains
    "fk_country": "fCouC",      # country, contains
    "fk_distance": "fDstU",     # distance, upto
    "fk_icao": "fIcoC",         # ICAO code, contains
    "fk_ismil": "fMilQ",        # is military?, equals
    "fk_operator": "fOpC",      # operator, contains
    "fk_regn": "fRegC",         # flight registration, contains
}

FLTR_RESPS = {
    "fr_icao": "Icao",          # flights's ICAO code
    "fr_to": "To",              # arrival airport
    "fr_from": "From",          # departure airport
    "fr_call": "Call",          # callsign
    "fr_latitude": "Lat",       # latitude
    "fr_longitude": "Long",     # longitude
    "fr_type": "Type",          # aircraft ICAO type
    "fr_mdl": "Mdl",            # aircraft model
    "fr_man": "Man",            # aircraft manufacturer
    "fr_operator": "Op",        # flight operator
    "fr_regn": "Reg",           # aircraft registration
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


def flights_get(lat=None, lng=None, airport=None, callsign=None,
                country=None, distance=None, icao=None, operator=None,
                regn=None):
    """Fetch flight(s) information from ADS-B Exchange. """
    fltr = {}

    if lat:
        fltr[FLTR_KEYS.get("fk_latitude")] = lat
    if lng:
        fltr[FLTR_KEYS.get("fk_longitude")] = lng
    if airport:
        fltr[FLTR_KEYS.get("fk_airport")] = airport
    if callsign:
        fltr[FLTR_KEYS.get("fk_callsign")] = callsign
    if country:
        fltr[FLTR_KEYS.get("fk_country")] = country
    if distance:
        fltr[FLTR_KEYS.get("fk_distance")] = distance
    if icao:
        fltr[FLTR_KEYS.get("fk_icao")] = icao
    if operator:
        fltr[FLTR_KEYS.get("fk_operator")] = operator
    if regn:
        fltr[FLTR_KEYS.get("fk_regn")] = regn

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

    flight_data = flights_get(country="United States", operator="Spirit")
    rflights = flights_refine(FLTR_RESPS.values(), flight_data)
    flights_print(rflights)

if __name__ == "__main__":
    main()
