"""
This module is responsible for pushing and pulling JSON data from/to the
backend and from/to files.
"""
import json
import requests
from werkzeug.datastructures import ImmutableMultiDict
from src.config_reader import ConfigReader

class JSONService:
    """
    This class encapsulates all requests made by the frontend to the backend.
    Most of the requests need to be done with `requests`, but some also act on
    local files.
    To use this class a jwt_token is required, otherwise the backend is not
    going to accept any requests.
    """

    def __init__(self, jwt_headers=None):
        """
        Initializing all necessary attributes.

        :param jwt_headers: jwt_token to be passed in the header of future\
        requests
        """
        self.jwt_headers = jwt_headers
        self.cfg_rdr = ConfigReader()
        self.connection = self.cfg_rdr.get_attr('backend_address')
        self.session = requests.Session()
        self.adapter = requests.adapters.HTTPAdapter(max_retries=10)
        self.session.mount('http://', self.adapter)

    def init(self, jwt_headers):
        """
        Useful for injecting the jwt_headers at a later time.
        """
        self.jwt_headers = jwt_headers

    def get(self, resource):
        """
        Returns the data from the specified resource.

        :param resource: JSON resource URI
        :returns: json data
        """
        return self.session.get(self.connection + resource,
                                headers=self.jwt_headers).json()

    def put(self, resource, data, exclude=[]):
        """
        Puts the data to the specified resource.

        :param resource: JSON resource URI
        :param data: data to be posted. has to be an `ImmutableMultiDict` which\
        are requests caught by flask.
        :param exclude: list of json keys which should be excluded
        :returns: raises an exception in case the request went wrong
        """
        copy = data.copy().to_dict()
        for item in exclude:
            copy.pop(item, None)

        resp = self.session.put(self.connection + resource, data=copy,
                                headers=self.jwt_headers)
        return resp.raise_for_status()

    def patch(self, resource, data, exclude=[]):
        """
        Patches the data to the specified resource.

        :param resource: JSON resource URI
        :param data: data to be posted. has to be an `ImmutableMultiDict` which\
        are requests caught by flask.
        :param exclude: list of json keys which should be excluded
        :returns: raises an exception in case the request went wrong
        """
        copy = data.copy().to_dict()
        for item in exclude:
            copy.pop(item, None)
        resp = self.session.patch(self.connection + resource, data=copy,
                                  headers=self.jwt_headers)
        return resp.raise_for_status()

    def write_json(self, data, filename='config/layout.json'):
        """
        Writes the data to a local json file.

        :param data: by default an `ImmutableMultiDict`, can also be a `dict`
        """

        if isinstance(data, ImmutableMultiDict):
            layout = data.copy().to_dict()
        else:
            layout = data
        with open(filename, 'w') as file:
            json.dump(layout, file)

    def read_json(self, filename, catch_exception=True):
        """
        Reads a local json file. If desired the exception that occurs in case
        the file does not exist may be caught internally and an `None` object
        may be returned.

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

    def patch_str(self, resource, data):
        """
        Patches the raw string data to the specified resource.

        :param resource: JSON resource URI
        :param data: data to be posted. has to be an `ImmutableMultiDict` which\
        are requests caught by flask.
        :param exclude: list of json keys which should be excluded
        :returns: raises an exception in case the request went wrong
        """
        json_data = json.load(data)
        resp = self.session.patch(self.connection + resource, data=json_data,
                             headers=self.jwt_headers)
        return resp.raise_for_status()

    @staticmethod
    def resp_to_dict(resp):
        """
        Transforms an `ImmutableMultiDict` into a regular `dict`.

        :param resp: `ImmutableMultiDict`
        :returns: boring, old `dict`
        """

        return resp.copy().to_dict()

if __name__ == '__main__':
    print('this does not work on its own')
