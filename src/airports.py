"""
Fetch information about airports.

Info includes ICAO and IATA codes, name, city, country, latitude and longitude.
"""

import logging
import json
import pprint
import requests

BASE_URL = "http://www.airport-data.com/api/ap_info.json?"
DB_FILE = "airports.json"
CODE_TYPES = ["icao", "iata"]
AIRPORT_DATA_STATUS_CODES = {
    200: "OK: All good",
    304: "NOT MODIFIED: No new data since last request",
    400: "BAD REQUEST: Invalid request",
    401: "UNAUTHORIZED: Authentication credentials are missing or incorrect",
    403: "FORBIDDEN: Valid request is refused",
    404: "NOT FOUND: Requested resource not found",
    406: "NOT ACCEPTABLE: Invalid format in request",
    410: "GONE: Resource is gone",
    429: "TOO MANY REQUESTS: API rate limit exceeded",
    500: "INTERNAL SERVER ERROR: Service is down",
    502: "BAD GATEWAY: Service is down",
    503: "SERVICE UNAVAILABLE: Service is busy",
}
LOG = logging.getLogger(__name__)


def __airport_url_get(code_type, code):
    airport_info = "%s=%s" % (code_type, code)
    airport_url = BASE_URL + airport_info
    return airport_url


def __airport_get(airport_query):
    try:
        resp = requests.get(airport_query)
    except requests.exceptions.RequestException:
        LOG.error("Fetching airport data failed", exc_info=1)

    airport_data = resp.json()
    status = airport_data['status']
    if status != 200:
        LOG.error("API returned error, %s", AIRPORT_DATA_STATUS_CODES[status])
        exit(0)

    return airport_data


def airport_read():
    """Read airport data from a local JSON file and return it in a dict. """
    try:
        with open(DB_FILE, "r") as filep:
            try:
                airport_data = json.load(filep)
            except ValueError:
                airport_data = {}
    except IOError:
        airport_data = {}

    return airport_data


def airport_write(airport_data):
    """Write the incoming airport_data dict to a local JSON file. """
    with open(DB_FILE, "wb") as filep:
        json.dump(airport_data, filep, indent=4)


def airport_get(code_type, code):
    """Fetch airport information. """
    code_type = code_type.lower()

    if code_type not in CODE_TYPES:
        raise ValueError("Invalid airport code type, %s", code_type)

    url = __airport_url_get(code_type, code)
    LOG.info("airport url: %s", url)

    jdats = __airport_get(url)
    keys = ["name", "location", "country_code", "latitude", "longitude",
            "icao", "iata"]
    airport = dict((key, jdats[key]) for key in keys if key in jdats)
    LOG.debug("airport data: %s", pprint.pformat(airport))
    return airport


def main():
    """Entry point if the module is used by itself. """
    log = logging.getLogger(__name__)
    format_str = "%(asctime)s %(name)-10s %(levelname)-5s %(message)s"
    logging.basicConfig(format=format_str)
    log.setLevel(logging.INFO)

    # Fetch airport data.
    airport_get("icao", "ksfo")
    airport_get("IATA", "maa")


if __name__ == "__main__":
    main()
