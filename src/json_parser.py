import requests
import json
from src.db_init import update_config

container_conn = 'http://localhost:12345'

def parse_json():
    info = requests.get(container_conn + '/info').json()
    temps = requests.get(container_conn + '/temp').json()
    filter = requests.get(container_conn + '/filter').json()
    fans_rel = requests.get(container_conn + '/fans/abs').json()
    pid = requests.get(container_conn + '/pid').json()
    # Joining the dicts
    return {**info, **temps, **filter, **fans_rel, **pid}

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
