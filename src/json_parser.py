import requests
import json

container_conn = 'http://localhost:12345'

def parse_json(resource='/cfg'):
    return requests.get(container_conn + resource).json()

def post_json(list):
    """
    Returns True if the POST action has been executed successfully.
    """
    copy = list.copy().to_dict()

    # removing artifacts from the POST request
    copy.pop('action', None)
    copy.pop('file', None)

    r = requests.post(container_conn, data=copy)
    return r.raise_for_status()

def resp_to_dict(resp):
    return resp.copy().to_dict()

if __name__ == '__main__':
    print(parse_json())
