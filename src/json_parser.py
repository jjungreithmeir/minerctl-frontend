"""
This module is responsible for pushing and pulling JSON data from/to the
backend and from files.
"""
import json
import requests
from src.config_reader import ConfigReader

CFG_RDR = ConfigReader()
CONTAINER_CONN = CFG_RDR.get_attr('backend_address')
SESSION = requests.Session()
ADAPTER = requests.adapters.HTTPAdapter(max_retries=10)
SESSION.mount('http://', ADAPTER)

def get(resource, headers):
    """
    Returns the data from the specified resource.

    :param resource: JSON resource URI
    :param headers: header containing JWT token for auth
    :returns: json data
    """
    return SESSION.get(CONTAINER_CONN + resource, headers=headers).json()

def put(resource, headers, data, exclude=[]):
    """
    Puts the data to the specified resource.

    :param resource: JSON resource URI
    :param headers: header containing JWT token for auth
    :param data: data to be posted. has to be an `ImmutableMultiDict` which are\
    requests caught by flask.
    :param exclude: list of json keys which should be excluded
    :returns: raises an exception in case the request went wrong
    """
    copy = data.copy().to_dict()
    for item in exclude:
        copy.pop(item, None)

    resp = SESSION.put(CONTAINER_CONN + resource, data=copy, headers=headers)
    return resp.raise_for_status()

def patch(resource, headers, data, exclude=[]):
    """
    Patches the data to the specified resource.

    :param resource: JSON resource URI
    :param headers: header containing JWT token for auth
    :param data: data to be posted. has to be an `ImmutableMultiDict` which are\
    requests caught by flask.
    :param exclude: list of json keys which should be excluded
    :returns: raises an exception in case the request went wrong
    """
    copy = data.copy().to_dict()
    for item in exclude:
        copy.pop(item, None)
    resp = SESSION.patch(CONTAINER_CONN + resource, data=copy, headers=headers)
    return resp.raise_for_status()

def write_json(data, filename='config/layout.json', needs_conversion=True):
    """
    Writes the data to a local json file.

    :param data: by default an `ImmutableMultiDict`. If a dict is to be saved\
    the `needs_conversion` TODO
    :param data: header containing JWT token for auth
    :param data: data to be posted. has to be an `ImmutableMultiDict` which are\
    requests caught by flask.
    :param exclude: list of json keys which should be excluded
    :returns: raises an exception in case the request went wrong
    """

    if needs_conversion:
        layout = data.copy().to_dict()
    else:
        layout = data
    with open(filename, 'w') as file:
        json.dump(layout, file)

def read_json(filename='config/layout.json', catch_exception=True):
    """
    Reads a local json file. If desired the exception that occurs in case the
    file does not exist may be caught internally and an `None` object may be
    returned.

    :param filename: JSON resource URI
    :param catch_exception: header containing JWT token for auth
    :returns: `dict` of json data
    :raises FileNotFoundError: if `catch_exception` is `false`
    """

    try:
        with open(filename) as file:
            data = json.load(file)
    except FileNotFoundError:
        if catch_exception:
            data = None
        else:
            raise FileNotFoundError
    return data

def patch_str(resource, headers, data):
    """
    Patches the raw string data to the specified resource.

    :param resource: JSON resource URI
    :param headers: header containing JWT token for auth
    :param data: data to be posted. has to be an `ImmutableMultiDict` which are\
    requests caught by flask.
    :param exclude: list of json keys which should be excluded
    :returns: raises an exception in case the request went wrong
    """
    json_data = json.load(data)
    resp = SESSION.patch(CONTAINER_CONN + resource, data=json_data,
                         headers=headers)
    return resp.raise_for_status()

def resp_to_dict(resp):
    """
    Transforms an `ImmutableMultiDict` into a regular `dict`.

    :param resp: `ImmutableMultiDict`
    :returns: boring, old `dict`
    """

    return resp.copy().to_dict()

if __name__ == '__main__':
    print('this does not work on its own')
