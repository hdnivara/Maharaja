"""
Utils for Maharaja.
"""

def csv_to_list(csv, delim=','):
    """
    Parses a string containing Comma-separated values into a list.

    csv     Comma-separated values.
            E.g., v1,v2,... --> [v1, v2, ...]
    """
    lst = csv.split(delim)
    return lst


def cskvp_to_dict(cskvp, delim=',', rdelim='='):
    """
    Parses a string containing Comma-separated key value pairs into a
    dictionary.

    cskvp   Comma-separated key value pairs
            E.g., k1=v1,k2=v2,... --> { k1 : v1, k2 : v2, k3 : v3, ... }
    """
    dct = {}
    for kvp in cskvp.split(delim):
        if kvp:
            (key, value) = kvp.split(rdelim)
            dct[key.strip()] = value.strip()
    return dct
