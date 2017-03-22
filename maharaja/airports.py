"""
Fetch information about airports.

Information includes name, city, country, ICAO/IATA codes and location
co-ordinates.

Airport data is obtained from http://www.airport-data.com/ service.
"""

import logging
import json
import requests

BASE_URL = "http://www.airport-data.com/api/ap_info.json?"
DB_FILE = "airports.json"
CODE_TYPES = ["icao",]
AIRPORT_DB = None
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


def __airport_db_load():
    """Read airport data from a local JSON file and return it in a dict. """
    global AIRPORT_DB

    try:
        with open(DB_FILE, "r") as filep:
            try:
                AIRPORT_DB = json.load(filep)
            except ValueError:
                AIRPORT_DB = {}
    except IOError:
        AIRPORT_DB = {}


def __airport_db_write(code, new_airport):
    """Write the incoming airport_data dict to a local JSON file. """
    AIRPORT_DB[code] = new_airport
    with open(DB_FILE, "wb") as filep:
        json.dump(AIRPORT_DB, filep, indent=4)


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


def __airport_remote_get(code_type, code):
    url = __airport_url_get(code_type, code)
    LOG.info("airport url: %s", url)

    jdats = __airport_get(url)
    keys = ["name", "location", "country_code", "latitude", "longitude",
            "icao", "iata"]
    remote_airport = dict((key, jdats[key]) for key in keys if key in jdats)
    return remote_airport


def __airport_local_get(airport_code):
    if AIRPORT_DB is None:
        __airport_db_load()

    if airport_code in AIRPORT_DB.keys():
        return AIRPORT_DB[airport_code]
    else:
        return None


def airport_get(code_type, code):
    """Fetch airport information.

    For a given airport code, fetch more data about the aiport. The data
    includes name, city, country, ICAO/IATA codes and location co-ordinates.

    Args:
        code_type (str): Type of airport code (e.g., ICAO)
        code (str): Airport code itself (e.g., VOMM)

    Returns:
        dict: airport data in a dict.
    """
    code_type = code_type.lower()
    code = code.upper()

    if code_type not in CODE_TYPES:
        raise ValueError("Invalid airport code type, %s", code_type)

    # Service the request locally, if possible.
    new_airport = __airport_local_get(code)

    if new_airport is None:
        LOG.debug("%s is requires remote service", code)

        # Airport data not available locally. Fetch it from the remote service.
        new_airport = __airport_remote_get(code_type, code)

        # Add the new airport's data to local database.
        __airport_db_write(code, new_airport)

    return new_airport


def main():
    """Entry point if the module is used by itself. """
    log = logging.getLogger(__name__)
    format_str = "%(asctime)s %(name)-10s %(levelname)-5s %(message)s"
    logging.basicConfig(format=format_str)
    log.setLevel(logging.INFO)

    # Fetch airport data.
    airport_get("icao", "ksfo")
    airport_get("icao", "vomm")


if __name__ == "__main__":
    main()
