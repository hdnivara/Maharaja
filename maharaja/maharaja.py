"""
Print or plot live flights.
"""
import logging
import sys

import argparse
import pprint

import adsbx
import airports
import utils

log = logging.getLogger(__name__)
fmt = "%(asctime)s %(name)-10s %(levelname)-5s %(message)s"
logging.basicConfig(format=fmt)
log.setLevel(logging.DEBUG)


def print_filters(filter_type):
    """Print the list of available filters and a short desc. """
    if filter_type is "map":
        filter_keys = adsbx.FLTR_MAPS.keys()
    elif filter_type is "print":
        filter_keys = adsbx.FLTR_RESPS.keys()
    elif filter_type is "flight":
        filter_keys = adsbx.FLTR_KEYS.keys()
    else:
        log.error("Unknown filter type, %s", filter_type)
        sys.exit(1)

    print "The following %s filters are supported:" % (filter_type)
    for key in filter_keys:
        if key in adsbx.FLTR_HELP:
            print "{:10}: {}".format(key, adsbx.FLTR_HELP[key])


def parse_args():
    """Parse arguments. """
    parser = argparse.ArgumentParser(description="Plot flight data on a map")

    parser.add_argument("-m", "--map", action="store_true", dest="map_flag",
                        help="Map flight data")
    mgrp = parser.add_mutually_exclusive_group()
    mgrp.add_argument("--map-attrs",
                      help="Map flight data with these attributes",
                      default="", metavar="v1,v2,...")
    mgrp.add_argument("--list-map-attrs", action="store_true",
                      help="List of available map attributes")

    parser.add_argument("-p", "--print", action="store_true",
                        dest="print_flag",
                        help="Map flight data")
    pgrp = parser.add_mutually_exclusive_group()
    pgrp.add_argument("--print-attrs",
                      help="Print flight data with these attributes",
                      default="", metavar="v1,v2,...")
    pgrp.add_argument("--list-print-attrs", action="store_true",
                      help="List of available print attributes")

    fgrp = parser.add_mutually_exclusive_group()
    fgrp.add_argument("--flight-filters",
                      help="Fetch flights matching this filter",
                      default="", metavar="k1=v1,k2=v2,...")
    fgrp.add_argument("--list-flight-filters", action="store_true",
                      help="List of available flight filters")

    args = parser.parse_args()

    if args.print_attrs and args.print_flag is False:
        raise parser.error("'-p | --print' is required for '--print-attrs'")

    if args.map_attrs and args.map_flag is False:
        raise parser.error("'-m | --map' is required for '--map-attrs'")

    return args

def airport_get(airport_code):
    """Get airport information. """
    return airports.airport_get("icao", airport_code)


def airport_db_create(flight_data):
    """Create an airport database/dict. """
    airports_db = {}

    airport_keys = ['From', 'To']
    for each_flight in flight_data:
        if all(key in each_flight for key in airport_keys):
            from_airport = each_flight['From'][:4]
            to_airport = each_flight['To'][:4]

            if from_airport not in airports_db.keys():
                airports_db[from_airport] = airport_get(from_airport)

            if to_airport not in airports_db.keys():
                airports_db[to_airport] = airport_get(to_airport)

    return airports_db


def flights_get(flight_fltr):
    """Get flight information. """
    flight_data = adsbx.flights_get(flight_fltr)
    return flight_data


def flights_refine(flight_data):
    """Refine flight information. """
    resp_fltr = adsbx.FLTR_RESPS.values()

    rflights = adsbx.flights_refine(resp_fltr, flight_data)
    return rflights


def flights_print(print_attr, flight_data):
    """Print flight information. """
    flights = adsbx.flights_str_get(print_attr, flight_data)
    return flights


def flights_map(map_attr, flight_data):
    """Plot flight data on a map. """

    airport_db_create(flight_data)


def main():
    """Entry point to the program. """

    args = parse_args()
    log.debug(pprint.pformat(args))

    if args.list_map_attrs:
        print_filters("map")
        sys.exit(0)

    if args.list_print_attrs:
        print_filters("print")
        sys.exit(0)

    if args.list_flight_filters:
        print_filters("flight")
        sys.exit(0)

    flight_fltr = utils.cskvp_to_dict(args.flight_filters)
    map_attr = utils.csv_to_list(args.map_attrs)
    print_attr = utils.csv_to_list(args.print_attrs)

    # Fetch flight information.
    flights = flights_get(flight_fltr)
    rflights = flights_refine(flights)

    # Print flight information.
    if args.print_flag:
        flights = flights_print(print_attr, rflights)
        print flights

    # Map flight data.
    if args.map_flag:
        flights_map(map_attr, rflights)

if __name__ == "__main__":
    main()
